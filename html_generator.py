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

import sys
import os

def render_prob_bar(label, pct, is_max=False):
    bar_color = "bg-blue-600 dark:bg-blue-500" if is_max else "bg-slate-300 dark:bg-slate-700"
    text_color = "text-blue-600 dark:text-blue-400 font-bold" if is_max else "text-slate-600 dark:text-slate-400"
    return f"""
    <div class="space-y-1">
        <div class="flex justify-between text-[11px] font-mono">
            <span class="{text_color}">{label}</span>
            <span class="{text_color}">{pct:.1f}%</span>
        </div>
        <div class="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div class="{bar_color} h-1.5 rounded-full transition-all duration-500" style="width: {pct:.1f}%"></div>
        </div>
    </div>
    """

def render_asset_card(asset_dict, badge_color):
    probs_html = ""
    max_pct = max(asset_dict["probabilities"].values())
    for lbl, pct in asset_dict["probabilities"].items():
        probs_html += render_prob_bar(lbl, pct, is_max=(pct == max_pct))
        
    feats_html = ""
    for k, v in asset_dict["features"].items():
        feats_html += f"""
        <div class="flex justify-between py-1.5 border-b border-[#E5DFD5]/70 dark:border-[#2C3E2F]/80 text-[11px] font-mono">
            <span class="text-[#756A5D] dark:text-[#A4B6A6]">{k}</span>
            <span class="font-bold text-[#2A241E] dark:text-[#F7F4EE]">{v}</span>
        </div>
        """
        
    # Monogram symbol for circular emblem
    symbol = "US" if "S&P" in asset_dict["asset"] else ("ID" if "IHSG" in asset_dict["asset"] else "₿")
    
    return f"""
    <!-- Card: {asset_dict['asset']} -->
    <div class="finviz-card arch-card bg-white dark:bg-[#1D2A1F] p-6 rounded-2xl border border-[#E5DFD5] dark:border-[#2C3E2F] shadow-sm flex flex-col justify-between space-y-5 transition-all hover:shadow-md">
        <div>
            <!-- Arched Header with Circular Seal Emblem -->
            <div class="flex items-center justify-between pb-4 border-b border-[#E5DFD5] dark:border-[#2C3E2F]">
                <div class="flex items-center gap-3">
                    <div class="seal-emblem w-9 h-9 text-xs">{symbol}</div>
                    <div>
                        <h3 class="text-base font-serif font-bold text-[#2A241E] dark:text-[#F7F4EE] leading-tight">{asset_dict['asset']}</h3>
                        <span class="text-[10px] font-mono text-[#756A5D] dark:text-[#A4B6A6] uppercase tracking-wider">{asset_dict['ticker']}</span>
                    </div>
                </div>
                <div class="text-right">
                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#A8522A]/10 dark:bg-[#D97343]/15 text-[#A8522A] dark:text-[#D97343] border border-[#A8522A]/20">
                        {asset_dict['confidence']:.1f}% P(Regime)
                    </span>
                </div>
            </div>

            <!-- Dominant Regime -->
            <div class="mt-3.5 p-3 rounded-xl bg-[#FAF7F2] dark:bg-[#19241B] border border-[#E5DFD5]/80 dark:border-[#2C3E2F]">
                <div class="text-[9px] uppercase font-mono tracking-wider text-[#756A5D] dark:text-[#A4B6A6] font-bold">Status Rezim Dominan (GMM EM)</div>
                <div class="text-sm font-serif font-bold text-[#A8522A] dark:text-[#D97343] mt-0.5">{asset_dict['dominant_regime']}</div>
            </div>

            <!-- Soft Probabilities -->
            <div class="mt-4 space-y-2.5">
                <div class="text-[10px] font-mono uppercase tracking-wider font-bold text-[#756A5D] dark:text-[#A4B6A6]">Distribusi Probabilitas Campuran (Soft Assignment)</div>
                {probs_html}
            </div>

            <!-- Features -->
            <div class="mt-4 pt-3.5 border-t border-[#E5DFD5] dark:border-[#2C3E2F]">
                <div class="text-[10px] font-mono uppercase tracking-wider font-bold text-[#756A5D] dark:text-[#A4B6A6] mb-1.5">Fitur Pilar Penggerak Rezim</div>
                <div class="space-y-0.5">
                    {feats_html}
                </div>
            </div>
        </div>

        <!-- Metrics & Stance Footer -->
        <div class="pt-3.5 border-t border-[#E5DFD5] dark:border-[#2C3E2F] space-y-2.5">
            <div class="flex items-center justify-between text-[10px] font-mono text-[#756A5D] dark:text-[#A4B6A6]">
                <span>Silhouette: <b class="text-[#2A241E] dark:text-[#F7F4EE]">{asset_dict['metrics']['silhouette_score']:.3f}</b></span>
                <span>DBI: <b class="text-[#2A241E] dark:text-[#F7F4EE]">{asset_dict['metrics']['davies_bouldin']:.2f}</b></span>
                <span>CHI: <b class="text-[#2A241E] dark:text-[#F7F4EE]">{asset_dict['metrics']['calinski_harabasz']:.1f}</b></span>
            </div>
            <div class="p-2.5 rounded-xl bg-[#A8522A]/10 dark:bg-[#D97343]/15 border border-[#A8522A]/20 dark:border-[#D97343]/25 text-[10px] font-mono text-[#A8522A] dark:text-[#D97343] font-medium leading-relaxed">
                <span class="font-bold">Direktif Risiko:</span> {asset_dict['quant_stance']}
            </div>
        </div>
    </div>
    """

def generate_tri_asset_hub_html(ml4t_data):
    c1 = render_asset_card(ml4t_data["sp500"], "bg-blue-500")
    c2 = render_asset_card(ml4t_data["ihsg"], "bg-emerald-500")
    c3 = render_asset_card(ml4t_data["bitcoin"], "bg-amber-500")
    
    return f"""
    <!-- ML4T BAB 1: TRI-ASSET REGIME CLASSIFIER (S&P 500, IHSG, BITCOIN) -->
    <div class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-[#1f2937] pb-3">
            <div>
                <div class="text-[11px] font-mono font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                    <span>Stefan Jansen &middot; Machine Learning for Trading (3rd Ed) &mdash; Bab 1: Deteksi Rezim Makro</span>
                </div>
                <h2 class="text-xl sm:text-2xl font-extrabold uppercase font-mono text-slate-900 dark:text-white mt-1">
                    Tri-Asset Unsupervised Market Regime Hub
                </h2>
                <p class="text-xs text-slate-600 dark:text-slate-400 font-mono mt-0.5">
                    Klasifikasi Gaussian Mixture Models (GMM) & Rantai Markov bebas look-ahead bias untuk S&P 500 (US), IHSG (Indonesia), dan Bitcoin (Kripto).
                </p>
            </div>
            <div class="flex items-center gap-2 font-mono text-xs">
                <span class="px-2.5 py-1 rounded bg-slate-100 dark:bg-[#161d27] border border-slate-300 dark:border-[#232e3d] text-slate-700 dark:text-slate-300 font-bold">
                    Algoritma: GMM EM (Full Covariance)
                </span>
            </div>
        </div>

        <!-- 3 Cards Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            {c1}
            {c2}
            {c3}
        </div>
    </div>
    """

def generate_tri_asset_risk_table_html(ml4t_data):
    rows_html = ""
    for asset_key, asset_name in [("sp500", "S&P 500 (US Macro)"), ("ihsg", "IHSG (Indonesia Emerging)"), ("bitcoin", "Bitcoin (Crypto Liquidity)")]:
        item = ml4t_data[asset_key]
        for row in item["historical_risk"]:
            ret_str = row["annual_return"]
            ret_color = "text-emerald-600 dark:text-emerald-400 font-bold" if "+" in ret_str else "text-rose-600 dark:text-rose-400 font-bold"
            rows_html += f"""
            <tr class="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-[#1d2736]">
                <td class="py-2.5 px-3 font-bold text-slate-900 dark:text-white">{asset_name}</td>
                <td class="py-2.5 px-3 text-slate-700 dark:text-slate-300">{row['regime']}</td>
                <td class="py-2.5 px-3 text-right text-slate-600 dark:text-slate-400">{row['months']} bln</td>
                <td class="py-2.5 px-3 text-right {ret_color}">{row['annual_return']}</td>
                <td class="py-2.5 px-3 text-right text-slate-700 dark:text-slate-300">{row['annual_vol']}</td>
                <td class="py-2.5 px-3 text-right text-rose-600 dark:text-rose-400 font-bold">{row['max_dd']}</td>
            </tr>
            """
            
    return f"""
    <!-- Matriks Evaluasi Risiko Empiris Kuantitatif Lintas Rezim -->
    <div class="finviz-card bg-white dark:bg-[#131922] p-5 rounded-lg border border-slate-200 dark:border-[#1f2937] shadow-sm space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200 dark:border-[#1f2937]">
            <div>
                <h3 class="text-sm font-extrabold uppercase font-mono text-slate-900 dark:text-white flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                    <span>Matriks Evaluasi Risiko Empiris Kuantitatif Lintas Rezim (ML4T Bab 1)</span>
                </h3>
                <p class="text-xs text-slate-500 dark:text-slate-400 font-mono mt-0.5">
                    Evaluasi volatilitas realisasi tahunan dan Maximum Drawdown pada data historis S&P 500, IHSG, dan Bitcoin.
                </p>
            </div>
            <span class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                Backtest 2005&ndash;2026
            </span>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs font-mono">
                <thead>
                    <tr class="border-b border-slate-200 dark:border-[#1f2937]">
                        <th class="py-2 px-3">Instrumen / Aset</th>
                        <th class="py-2 px-3">Rezim Terklasifikasi</th>
                        <th class="py-2 px-3 text-right">Durasi Sampel</th>
                        <th class="py-2 px-3 text-right">Return Tahunan (p.a.)</th>
                        <th class="py-2 px-3 text-right">Volatilitas (p.a.)</th>
                        <th class="py-2 px-3 text-right">Max Drawdown</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    """

def generate_curriculum_tab_html(ml4t_data):
    parts_html = ""
    for p in ml4t_data["curriculum"]:
        chapters_grid = ""
        for ch in p["chapters"]:
            if ch["status"] == "LIVE ACTIVE":
                badge = '<span class="px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">LIVE ACTIVE</span>'
            elif ch["status"] == "ACTIVE":
                badge = '<span class="px-2 py-0.5 rounded text-[9px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400 border border-blue-500/30">ACTIVE</span>'
            elif ch["status"] == "INTEGRATED":
                badge = '<span class="px-2 py-0.5 rounded text-[9px] font-bold bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30">INTEGRATED</span>'
            else:
                badge = '<span class="px-2 py-0.5 rounded text-[9px] font-bold bg-slate-500/15 text-slate-600 dark:text-slate-400 border border-slate-500/30">PLANNED</span>'
                
            chapters_grid += f"""
            <div class="p-3.5 rounded-lg bg-slate-50 dark:bg-[#17202c] border border-slate-200 dark:border-[#233042] flex flex-col justify-between space-y-2">
                <div>
                    <div class="flex items-center justify-between gap-1 mb-1 font-mono">
                        <span class="text-[10px] font-extrabold text-blue-600 dark:text-blue-400">BAB {ch['no']:02d}</span>
                        {badge}
                    </div>
                    <div class="text-xs font-bold text-slate-900 dark:text-white font-mono">{ch['title']}</div>
                    <p class="text-[11px] text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">{ch['detail']}</p>
                </div>
                <div class="flex items-center gap-1.5 pt-2 border-t border-slate-200/60 dark:border-[#233042]/80 text-[9px] font-mono text-slate-500">
                    <span class="px-1 rounded bg-slate-200 dark:bg-slate-800">S&P 500</span>
                    <span class="px-1 rounded bg-slate-200 dark:bg-slate-800">IHSG</span>
                    <span class="px-1 rounded bg-slate-200 dark:bg-slate-800">BTC</span>
                </div>
            </div>
            """
            
        parts_html += f"""
        <div class="finviz-card bg-white dark:bg-[#131922] p-5 rounded-lg border border-slate-200 dark:border-[#1f2937] shadow-sm space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-[#1f2937]">
                <h3 class="text-xs font-extrabold font-mono text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                    <span>{p['part']}</span>
                </h3>
                <span class="text-[10px] font-mono text-slate-500 dark:text-slate-400">5 Bab Terstruktur</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {chapters_grid}
            </div>
        </div>
        """
        
    return f"""
    <!-- TAB 2: ML4T 27 CHAPTERS CURRICULUM & QUANTITATIVE MODELS -->
    <div id="tab-ml4t" class="tab-pane hidden space-y-6">
        <div class="finviz-card bg-white dark:bg-[#131922] p-6 rounded-lg border border-slate-200 dark:border-[#1f2937] shadow-sm">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-[#1f2937]">
                <div class="space-y-1">
                    <div class="text-[11px] font-mono font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                        <span>Peta Jalan Kuantitatif End-to-End</span>
                    </div>
                    <h2 class="text-xl sm:text-2xl font-extrabold uppercase font-mono text-slate-900 dark:text-white">
                        Kurikulum Machine Learning for Trading (Stefan Jansen 3rd Ed) &mdash; 27 Bab
                    </h2>
                    <p class="text-xs text-slate-600 dark:text-slate-400 font-mono">
                        Struktur sistematis 5 bagian dari data, rekayasa fitur, pemodelan ML/DL, simulasi portofolio, hingga live trading & MLOps lintas aset (S&P 500, IHSG, BTC).
                    </p>
                </div>
                <div class="flex items-center gap-2 font-mono text-xs">
                    <span class="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-bold">
                        Bab 1: Live Terintegrasi
                    </span>
                    <span class="px-2.5 py-1 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 font-bold">
                        Multi-Asset: US &bull; ID &bull; Crypto
                    </span>
                </div>
            </div>

            <!-- 5 Parts Sections -->
            <div class="mt-6 space-y-6">
                {parts_html}
            </div>
        </div>
    </div>
    """




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
    # ML4T Multi-Asset Regimes & Curriculum
    from ml4t_regime_engine import get_tri_asset_regimes
    ml4t_data = payload.get("ml4t_regimes") or get_tri_asset_regimes(snapshot=payload, prices=prices, indo_macro=indo_macro)
    tri_asset_hub_html = generate_tri_asset_hub_html(ml4t_data)
    tri_asset_risk_table_html = generate_tri_asset_risk_table_html(ml4t_data)
    curriculum_tab_html = generate_curriculum_tab_html(ml4t_data)


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

    # Extract dynamic unique news sources by occurrence frequency
    from collections import Counter
    raw_sources = [n.get('source') for n in (global_news + geopolitics_news + crypto_news + indonesia_news) if n.get('source')]
    source_counts = Counter(raw_sources)
    top_sources = [s for s, _ in source_counts.most_common(8)]
    active_news_sources_str = ", ".join(top_sources) if top_sources else "Reuters, Bloomberg, CoinDesk, CNBC Indonesia, FXStreet"

    # Market session & weekend status
    import datetime
    wib_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    is_weekend = wib_now.strftime("%A") in ["Saturday", "Sunday"]
    if is_weekend:
        session_pill_html = '<div id="market-session-pill" class="hidden sm:inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-950 text-amber-300 border border-amber-700/50">WEEKEND CLOSE (PASAR TUTUP)</div>'
    else:
        session_pill_html = '<div id="market-session-pill" class="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950 text-sprout border border-emerald-700/50">LIVE SESSION ACTIVE</div>'
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

    def clean_driver_text(d_text):
        if not d_text:
            return ""
        for marker in [
            "Berita pasar terkait:",
            "Berita terkait (bukan klaim sebab):",
            "Berita terkait:",
            "Tidak ada berita relevan yang selaras arah di feed saat ini."
        ]:
            if marker in d_text:
                d_text = d_text.split(marker)[0].strip()
        return d_text.rstrip(". ") + "." if d_text else ""

    def render_news_pill(news_dict):
        if not news_dict or not news_dict.get("available"):
            return '<div class="p-2 rounded-xl bg-white/60 border border-linen-200 text-[11px] text-stone-400 italic font-mono">Tidak ada berita terkait yang selaras arah di feed saat ini.</div>'
        t = str(news_dict.get("title", "")).replace('"', "&quot;")
        s = str(news_dict.get("source", ""))
        l = str(news_dict.get("link", "#"))
        return f'''<a href="{l}" target="_blank" class="block p-2 rounded-xl bg-white/80 border border-linen-300 text-[11px] text-stone-600 hover:text-forest-900 hover:border-forest-600 transition-all">
            <span class="font-bold text-forest-800">Berita Terkait:</span> "{t}" 
            <span class="font-mono text-stone-400">({s}) &#x2197;</span>
        </a>'''

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
    <title>ML4T &middot; Machine Learning for Trading | Tri-Asset Quantitative Terminal</title>
    <!-- Google Fonts: Cormorant Garamond (Luxury Editorial Serif), Playfair Display, Inter & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,400;1,600&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,400;1,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        serif: ['"Cormorant Garamond"', '"Playfair Display"', 'Georgia', 'serif'],
                        display: ['"Playfair Display"', '"Cormorant Garamond"', 'Georgia', 'serif'],
                        sans: ['"Inter"', 'system-ui', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }},
                    colors: {{
                        terracotta: {{
                            50: '#FBF5F2',
                            100: '#F4EAE4',
                            200: '#E8D2C5',
                            500: '#C26335',
                            600: '#A8522A',
                            700: '#8F421D',
                        }},
                        forest: {{
                            800: '#223223',
                            900: '#162118',
                            950: '#0F1710',
                        }},
                        linen: {{
                            50: '#FAF8F4',
                            100: '#F7F4EE',
                            200: '#EFEAE0',
                            300: '#E5DFD5',
                            400: '#D5CBBF',
                        }}
                    }}
                }}
            }}
        }};

        // Instant Theme Detection to prevent theme flicker
        (function() {{
            const savedTheme = localStorage.getItem('finviz_theme');
            if (savedTheme === 'dark') {{
                document.documentElement.classList.add('dark');
            }} else {{
                document.documentElement.classList.remove('dark');
            }}
        }})();
    </script>
    <style>
        :root {{
            --font-serif: 'Cormorant Garamond', 'Playfair Display', Georgia, serif;
            --font-display: 'Playfair Display', 'Cormorant Garamond', Georgia, serif;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}

        html.dark {{
            color-scheme: dark;
        }}
        html:not(.dark) {{
            color-scheme: light;
        }}

        body {{
            font-family: var(--font-sans);
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.2s ease, color 0.2s ease;
        }}

        /* Light Mode Base: Warm Linen & Terracotta (Rio Minimalist Aesthetic) */
        html:not(.dark) body {{
            background-color: #F7F4EE;
            color: #2A241E;
        }}

        /* Dark Mode Base: Deep Forest Olive Green (Image 5 Aesthetic) */
        html.dark body {{
            background-color: #162118;
            color: #F7F4EE;
        }}

        /* Cards & Containers */
        .finviz-card, .natural-card {{
            border-radius: 0.75rem;
            transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        html:not(.dark) .finviz-card, html:not(.dark) .natural-card {{
            background-color: #FFFDFB !important;
            border: 1px solid #E5DFD5 !important;
            color: #2A241E;
            box-shadow: 0 1px 3px rgba(42, 36, 30, 0.04), 0 4px 14px rgba(42, 36, 30, 0.02);
        }}
        html.dark .finviz-card, html.dark .natural-card {{
            background-color: #1D2A1F !important;
            border: 1px solid #2C3E2F !important;
            color: #F7F4EE;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
        }}

        /* Inner Panels & Sub-boxes */
        html:not(.dark) .bg-linen-50, html:not(.dark) .bg-slate-50 {{ background-color: #FAF7F2 !important; }}
        html:not(.dark) .bg-linen-100, html:not(.dark) .bg-slate-100 {{ background-color: #F2EDE4 !important; }}
        html:not(.dark) .border-linen-200, html:not(.dark) .border-slate-200 {{ border-color: #E5DFD5 !important; }}
        html:not(.dark) .border-linen-300, html:not(.dark) .border-slate-300 {{ border-color: #D8D1C4 !important; }}
        html:not(.dark) .bg-white {{ background-color: #FFFDFB !important; }}

        html.dark .bg-linen-50, html.dark .bg-slate-50 {{ background-color: #19241B !important; }}
        html.dark .bg-linen-100, html.dark .bg-slate-100 {{ background-color: #223124 !important; }}
        html.dark .border-linen-200, html.dark .border-slate-200 {{ border-color: #2C3E2F !important; }}
        html.dark .border-linen-300, html.dark .border-slate-300 {{ border-color: #384F3C !important; }}
        html.dark .bg-white {{ background-color: #1D2A1F !important; }}

        /* Typography & Headings */
        html:not(.dark) .text-forest-900, html:not(.dark) .text-slate-900 {{ color: #2A241E !important; }}
        html:not(.dark) .text-forest-800, html:not(.dark) .text-slate-800 {{ color: #3F372E !important; }}
        html:not(.dark) .text-forest-700, html:not(.dark) .text-slate-700 {{ color: #5B5044 !important; }}
        html:not(.dark) .text-stone-900 {{ color: #2A241E !important; }}
        html:not(.dark) .text-stone-800 {{ color: #3F372E !important; }}
        html:not(.dark) .text-stone-700 {{ color: #5B5044 !important; }}
        html:not(.dark) .text-stone-600, html:not(.dark) .text-slate-600 {{ color: #756A5D !important; }}
        html:not(.dark) .text-stone-500, html:not(.dark) .text-slate-500 {{ color: #8F8273 !important; }}
        html:not(.dark) .text-stone-400, html:not(.dark) .text-slate-400 {{ color: #A89B8C !important; }}
        html:not(.dark) .text-sage-600, html:not(.dark) .text-blue-600 {{ color: #A8522A !important; }}
        html:not(.dark) .text-sage-700, html:not(.dark) .text-blue-700 {{ color: #8F421D !important; }}
        html:not(.dark) .text-sprout {{ color: #A8522A !important; }}

        html.dark .text-forest-900, html.dark .text-slate-900 {{ color: #F7F4EE !important; }}
        html.dark .text-forest-800, html.dark .text-slate-800 {{ color: #EAE4DA !important; }}
        html.dark .text-forest-700, html.dark .text-slate-700 {{ color: #C5BCB0 !important; }}
        html.dark .text-stone-900 {{ color: #F7F4EE !important; }}
        html.dark .text-stone-800 {{ color: #EAE4DA !important; }}
        html.dark .text-stone-700 {{ color: #C5BCB0 !important; }}
        html.dark .text-stone-600, html.dark .text-slate-600 {{ color: #A4B6A6 !important; }}
        html.dark .text-stone-500, html.dark .text-slate-500 {{ color: #829684 !important; }}
        html.dark .text-stone-400, html.dark .text-slate-400 {{ color: #697D6B !important; }}
        html.dark .text-sage-600, html.dark .text-blue-600 {{ color: #D97343 !important; }}
        html.dark .text-sage-700, html.dark .text-blue-700 {{ color: #EA8455 !important; }}
        html.dark .text-sprout {{ color: #D97343 !important; }}

        /* Navigation Tabs */
        .tab-btn {{
            font-family: var(--font-mono);
            border-radius: 0.5rem;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
        }}
        html:not(.dark) .tab-btn.active {{
            background-color: #A8522A !important;
            color: #FFFFFF !important;
            border-color: #8F421D !important;
            box-shadow: 0 2px 8px rgba(168, 82, 42, 0.25);
        }}
        html:not(.dark) .tab-btn:not(.active) {{
            background-color: #FFFDFB !important;
            color: #756A5D !important;
            border: 1px solid #E5DFD5 !important;
        }}
        html:not(.dark) .tab-btn:not(.active):hover {{
            background-color: #F2ECE2 !important;
            color: #2A241E !important;
            border-color: #D8D1C4 !important;
        }}

        html.dark .tab-btn.active {{
            background-color: #D97343 !important;
            color: #FFFFFF !important;
            border-color: #EA8455 !important;
            box-shadow: 0 2px 10px rgba(217, 115, 67, 0.35);
        }}
        html.dark .tab-btn:not(.active) {{
            background-color: #1D2A1F !important;
            color: #A4B6A6 !important;
            border: 1px solid #2C3E2F !important;
        }}
        html.dark .tab-btn:not(.active):hover {{
            background-color: #27392A !important;
            color: #F7F4EE !important;
            border-color: #384F3C !important;
        }}

        /* Table Styling */
        table {{ border-collapse: collapse; }}
        html:not(.dark) table th {{
            background-color: #F2ECE2 !important;
            color: #5B5044 !important;
            border-bottom: 1px solid #D8D1C4 !important;
            font-family: var(--font-mono);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        html:not(.dark) table tbody tr:nth-child(even) {{ background-color: #FAF7F2; }}
        html:not(.dark) table tbody tr:nth-child(odd) {{ background-color: #FFFDFB; }}
        html:not(.dark) table tbody tr:hover {{ background-color: #F4EFE6 !important; }}

        html.dark table th {{
            background-color: #223124 !important;
            color: #A4B6A6 !important;
            border-bottom: 1px solid #2C3E2F !important;
            font-family: var(--font-mono);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        html.dark table tbody tr:nth-child(even) {{ background-color: #172219; }}
        html.dark table tbody tr:nth-child(odd) {{ background-color: #1D2A1F; }}
        html.dark table tbody tr:hover {{ background-color: #263829 !important; }}

        /* Terracotta Circular Emblem Seal (like RS in Image 1 & emblems in Image 2) */
        .seal-emblem {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 9999px;
            background-color: #A8522A;
            color: #FFFFFF;
            font-family: var(--font-serif);
            font-weight: 700;
            box-shadow: 0 0 0 2px #FFFDFB, 0 0 0 3.5px #A8522A;
        }}
        html.dark .seal-emblem {{
            background-color: #D97343;
            box-shadow: 0 0 0 2px #162118, 0 0 0 3.5px #D97343;
        }}

        /* Arched Card Styling (like Image 3 & 4) */
        .arch-card {{
            border-top-left-radius: 2rem !important;
            border-top-right-radius: 2rem !important;
        }}

        /* Footer */
        html:not(.dark) footer {{
            background-color: #F2ECE2 !important;
            border-color: #E5DFD5 !important;
            color: #756A5D !important;
        }}
        html.dark footer {{
            background-color: #111A13 !important;
            border-color: #2C3E2F !important;
            color: #A4B6A6 !important;
        }}

        /* WhatsApp Box */
        html:not(.dark) #wa-text-content {{
            background-color: #FAF7F2 !important;
            color: #A8522A !important;
            border-color: #E5DFD5 !important;
        }}
        html.dark #wa-text-content {{
            background-color: #111A13 !important;
            color: #E07A4A !important;
            border-color: #2C3E2F !important;
        }}

        /* Finviz Flashes */
        @keyframes flashGreen {{
            0% {{ background-color: rgba(46, 107, 62, 0.35); }}
            100% {{ background-color: transparent; }}
        }}
        @keyframes flashRed {{
            0% {{ background-color: rgba(166, 58, 43, 0.35); }}
            100% {{ background-color: transparent; }}
        }}
        .flash-up {{ animation: flashGreen 1s ease-out; }}
        .flash-down {{ animation: flashRed 1s ease-out; }}

        /* Custom Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        html:not(.dark) ::-webkit-scrollbar-track {{ background: #F7F4EE; }}
        html:not(.dark) ::-webkit-scrollbar-thumb {{ background: #D8D1C4; border-radius: 9999px; }}
        html.dark ::-webkit-scrollbar-track {{ background: #162118; }}
        html.dark ::-webkit-scrollbar-thumb {{ background: #2C3E2F; border-radius: 9999px; }}
    </style>
</head>
<body class="bg-[#F7F4EE] text-[#2A241E] dark:bg-[#162118] dark:text-[#F7F4EE] min-h-screen font-sans transition-colors">

    <!-- TOP EDITORIAL STATUS & TICKER BAR -->
    <header class="bg-[#F2EDE4] dark:bg-[#111A13] text-[#2A241E] dark:text-[#F7F4EE] text-xs border-b border-[#E5DFD5] dark:border-[#2C3E2F] py-2 px-4 sm:px-8 transition-colors">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
            <!-- Brand & Emblem -->
            <div class="flex items-center gap-3">
                <div class="seal-emblem w-7 h-7 text-[11px] tracking-widest">4T</div>
                <div class="flex items-center gap-2">
                    <span class="font-serif font-bold tracking-wider text-sm text-[#2A241E] dark:text-[#F7F4EE] uppercase">ML4T QUANTITATIVE</span>
                    <span class="text-[#8F8273] dark:text-[#697D6B] hidden sm:inline font-mono">|</span>
                    <span class="text-[#756A5D] dark:text-[#A4B6A6] hidden sm:inline text-xs font-mono">Tri-Asset Universe: S&P 500 &middot; IHSG &middot; Bitcoin</span>
                </div>
            </div>

            <!-- Clocks, Session & Dark/Light Switcher -->
            <div class="flex items-center gap-3 text-xs font-mono">
                <div class="flex items-center gap-1.5 bg-[#FAF7F2] dark:bg-[#19241B] px-2.5 py-1 rounded-md border border-[#E5DFD5] dark:border-[#2C3E2F]">
                    <span class="text-[#756A5D] dark:text-[#A4B6A6]">WIB:</span>
                    <span id="live-clock-wib" class="font-bold text-[#2A241E] dark:text-[#F7F4EE]">--:--:--</span>
                </div>
                <div class="flex items-center gap-1.5 bg-[#FAF7F2] dark:bg-[#19241B] px-2.5 py-1 rounded-md border border-[#E5DFD5] dark:border-[#2C3E2F]">
                    <span id="ny-tz-label" class="text-[#756A5D] dark:text-[#A4B6A6]">NYC:</span>
                    <span id="live-clock-est" class="font-bold text-[#2A241E] dark:text-[#F7F4EE]">--:--:--</span>
                </div>
                {session_pill_html}

                <!-- Dark Mode / Light Mode Switcher Button -->
                <button id="theme-toggle" onclick="toggleFinvizTheme()" class="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-bold transition-all border border-[#E5DFD5] dark:border-[#2C3E2F] bg-[#FAF7F2] dark:bg-[#19241B] text-[#2A241E] dark:text-[#F7F4EE] hover:bg-[#EBE5DA] dark:hover:bg-[#223124] cursor-pointer shadow-sm" title="Toggle Dark/Light Mode">
                    <span id="theme-icon">🌙</span>
                    <span id="theme-label" class="uppercase tracking-wider">DARK</span>
                </button>
            </div>
        </div>
    </header>

    <!-- WARM EDITORIAL HERO & MARKET TICKER TILES -->
    <section class="border-b border-[#E5DFD5] dark:border-[#2C3E2F] bg-[#FFFDFB] dark:bg-[#18231A] px-4 sm:px-8 py-6 transition-colors">
        <div class="max-w-7xl mx-auto space-y-5">
            <!-- Header Row -->
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
                <div class="space-y-1.5 max-w-3xl">
                    <div class="inline-flex items-center gap-2 px-3 py-0.5 rounded-full text-[11px] font-mono bg-[#A8522A]/10 dark:bg-[#D97343]/15 text-[#A8522A] dark:text-[#D97343] border border-[#A8522A]/20 font-bold">
                        <span class="w-2 h-2 rounded-full bg-[#A8522A] dark:bg-[#D97343] animate-pulse"></span>
                        <span>Stefan Jansen (3rd Ed) &middot; Marcos L&oacute;pez de Prado &middot; Database: <b class="font-mono text-[#2A241E] dark:text-[#F7F4EE]">{display_date}</b></span>
                    </div>
                    <h1 class="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold tracking-tight text-[#2A241E] dark:text-[#F7F4EE] leading-tight">
                        Machine Learning for Trading &middot; <span class="italic font-normal">Tri-Asset Terminal</span>
                    </h1>
                    <p class="text-xs sm:text-sm text-[#756A5D] dark:text-[#A4B6A6] leading-relaxed">
                        Arsitektur sistematis 27 bab pemodelan kuantitatif: Deteksi Rezim GMM tak bersyarat, rekayasa fitur alpha, dan alokasi risiko empiris lintas Wall Street (S&P 500), Pasar Domestik (IHSG), dan Aset Digital (Bitcoin).
                    </p>
                </div>
                <div class="flex items-center gap-3 font-mono text-xs">
                    <button onclick="refreshAllData()" class="flex items-center gap-2 px-4 py-2 rounded-lg font-bold bg-[#A8522A] hover:bg-[#8F421D] dark:bg-[#D97343] dark:hover:bg-[#EA8455] text-white transition-all shadow cursor-pointer">
                        <span id="sync-icon">🔄</span>
                        <span id="btn-refresh-text">Refresh Data Pasar</span>
                    </button>
                    <a href="https://github.com/studikarangsambung/macro-pulse" target="_blank" class="flex items-center gap-1.5 px-3.5 py-2 rounded-lg font-medium bg-[#F2EDE4] dark:bg-[#223124] text-[#2A241E] dark:text-[#F7F4EE] border border-[#E5DFD5] dark:border-[#2C3E2F] hover:bg-[#EBE5DA] dark:hover:bg-[#2B3E2E] transition-all">
                        <span>GitHub</span> ↗
                    </a>
                </div>
            </div>

            <!-- 6 Key Assets Ticker Strip (Arched Window Minimalist Cards) -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-1">
                <!-- BTC Live -->
                <div class="p-3.5 rounded-xl bg-[#FAF7F2] dark:bg-[#1D2A1F] border border-[#E5DFD5] dark:border-[#2C3E2F] transition-all shadow-sm hover:border-[#A8522A]/50" id="card-btc">
                    <div class="flex items-center justify-between text-[11px] text-[#756A5D] dark:text-[#A4B6A6] font-mono">
                        <span class="font-bold flex items-center gap-1 text-[#2A241E] dark:text-[#F7F4EE]">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>BTC / USD
                        </span>
                        <span class="text-[9px] uppercase px-1 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold">Live</span>
                    </div>
                    <div class="mt-1.5 flex items-baseline justify-between font-mono">
                        <div id="live-btc" class="text-base font-extrabold text-[#2A241E] dark:text-[#F7F4EE] font-mono">${prices.get('BTC-USD', {}).get('close', 0):,.0f}</div>
                        <div id="live-btc-chg" class="text-xs font-semibold">{chg_badge(prices.get('BTC-USD', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

                <!-- ETH Live -->
                <div class="p-3.5 rounded-xl bg-[#FAF7F2] dark:bg-[#1D2A1F] border border-[#E5DFD5] dark:border-[#2C3E2F] transition-all shadow-sm hover:border-[#A8522A]/50" id="card-eth">
                    <div class="flex items-center justify-between text-[11px] text-[#756A5D] dark:text-[#A4B6A6] font-mono">
                        <span class="font-bold flex items-center gap-1 text-[#2A241E] dark:text-[#F7F4EE]">
                            <span class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>ETH / USD
                        </span>
                        <span class="text-[9px] uppercase px-1 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 font-bold">Live</span>
                    </div>
                    <div class="mt-1.5 flex items-baseline justify-between font-mono">
                        <div id="live-eth" class="text-base font-extrabold text-[#2A241E] dark:text-[#F7F4EE] font-mono">${prices.get('ETH-USD', {}).get('close', 0):,.0f}</div>
                        <div id="live-eth-chg" class="text-xs font-semibold">{chg_badge(prices.get('ETH-USD', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

                <!-- IHSG Spot (^JKSE) -->
                <div class="p-3.5 rounded-xl bg-[#FAF7F2] dark:bg-[#1D2A1F] border border-[#E5DFD5] dark:border-[#2C3E2F] transition-all shadow-sm">
                    <div class="flex items-center justify-between text-[11px] text-[#756A5D] dark:text-[#A4B6A6] font-mono">
                        <span class="font-bold text-[#2A241E] dark:text-[#F7F4EE]">IHSG (^JKSE)</span>
                        <span class="text-[9px] uppercase px-1 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold">{indo_macro.get('ihsg_status', 'Spot')}</span>
                    </div>
                    <div class="mt-1.5 flex items-baseline justify-between font-mono">
                        <div class="text-base font-extrabold text-[#2A241E] dark:text-[#F7F4EE] font-mono">
                            {f"{indo_macro['ihsg_val']:,.2f}" if indo_macro.get('ihsg_val') else "N/A"}
                        </div>
                        <div class="text-xs font-semibold">{chg_badge(indo_macro.get('ihsg_chg', 0))}</div>
                    </div>
                </div>

                <!-- USD / IDR -->
                <div class="p-3.5 rounded-xl bg-[#FAF7F2] dark:bg-[#1D2A1F] border border-[#E5DFD5] dark:border-[#2C3E2F] transition-all shadow-sm">
                    <div class="flex items-center justify-between text-[11px] text-[#756A5D] dark:text-[#A4B6A6] font-mono">
                        <span class="font-bold text-[#2A241E] dark:text-[#F7F4EE]">USD / IDR</span>
                        <span class="text-[9px] uppercase px-1 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold">{indo_macro.get('kurs_status', 'Kurs')}</span>
                    </div>
                    <div class="mt-1.5 flex items-baseline justify-between font-mono">
                        <div class="text-base font-extrabold text-[#2A241E] dark:text-[#F7F4EE] font-mono">{f"Rp {prices['USDIDR=X']['close']:,.0f}" if prices.get('USDIDR=X', {}).get('close') else "N/A"}</div>
                        <div class="text-xs font-semibold">{chg_badge(prices.get('USDIDR=X', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

                <!-- XAUUSD (Gold Spot) -->
                <div class="p-3.5 rounded-xl bg-[#FAF7F2] dark:bg-[#1D2A1F] border border-[#E5DFD5] dark:border-[#2C3E2F] transition-all shadow-sm">
                    <div class="flex items-center justify-between text-[11px] text-[#756A5D] dark:text-[#A4B6A6] font-mono">
                        <span class="font-bold text-[#2A241E] dark:text-[#F7F4EE]">Emas (XAUUSD)</span>
                        <span class="text-[9px] uppercase px-1 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold">Spot</span>
                    </div>
                    <div class="mt-1.5 flex items-baseline justify-between font-mono">
                        <div class="text-base font-extrabold text-[#2A241E] dark:text-[#F7F4EE] font-mono">{f"${prices['GC=F']['close']:,.1f}" if prices.get('GC=F', {}).get('close') else "N/A"}</div>
                        <div class="text-xs font-semibold">{chg_badge(prices.get('GC=F', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>

                <!-- US 10Y Yield -->
                <div class="p-3.5 rounded-xl bg-[#FAF7F2] dark:bg-[#1D2A1F] border border-[#E5DFD5] dark:border-[#2C3E2F] transition-all shadow-sm">
                    <div class="flex items-center justify-between text-[11px] text-[#756A5D] dark:text-[#A4B6A6] font-mono">
                        <span class="font-bold text-[#2A241E] dark:text-[#F7F4EE]">US 10Y Yield</span>
                        <span class="text-[9px] uppercase px-1 rounded bg-rose-500/10 text-rose-600 dark:text-rose-400 font-bold">Yield</span>
                    </div>
                    <div class="mt-1.5 flex items-baseline justify-between font-mono">
                        <div class="text-base font-extrabold text-[#2A241E] dark:text-[#F7F4EE] font-mono">{f"{prices['^TNX']['close']:.3f}%" if prices.get('^TNX', {}).get('close') else "N/A"}</div>
                        <div class="text-xs font-semibold">{chg_badge(prices.get('^TNX', {}).get('change_1d_pct', 0))}</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- EXACT 7 ML4T NAVIGATION TABS (USER SPECIFICATION) -->
    <nav class="sticky top-0 z-30 bg-[#F7F4EE]/95 dark:bg-[#162118]/95 backdrop-blur-md border-b border-[#E5DFD5] dark:border-[#2C3E2F] px-4 sm:px-8 py-2.5 transition-colors">
        <div class="max-w-7xl mx-auto flex items-center gap-1.5 overflow-x-auto no-scrollbar font-mono text-xs">
            <button onclick="switchTab('tab-overview')" id="btn-tab-overview" class="tab-btn active px-3.5 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap">
                Tab 1: Hub Rezim Tri-Asset (Bab 1)
            </button>
            <button onclick="switchTab('tab-ml4t')" id="btn-tab-ml4t" class="tab-btn px-3.5 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap">
                Tab 2: Kurikulum 27 Bab ML4T (Peta Jalan Stefan Jansen)
            </button>
            <button onclick="switchTab('tab-flow')" id="btn-tab-flow" class="tab-btn px-3.5 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap">
                Tab 3: Flow Projection (7–30D)
            </button>
            <button onclick="switchTab('tab-calendar')" id="btn-tab-calendar" class="tab-btn px-3.5 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap">
                Tab 4: Kalender Ekonomi DST
            </button>
            <button onclick="switchTab('tab-sectors')" id="btn-tab-sectors" class="tab-btn px-3.5 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap">
                Tab 5: Rotasi 11 Sektor US
            </button>
            <button onclick="switchTab('tab-indonesia')" id="btn-tab-indonesia" class="tab-btn px-3.5 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap">
                Tab 6: Transmisi Makro Indonesia
            </button>
            <button onclick="switchTab('tab-wa')" id="btn-tab-wa" class="tab-btn px-3.5 py-1.5 rounded-lg font-bold transition-all whitespace-nowrap">
                Tab 7: WhatsApp Quant Broadcast
            </button>
        </div>
    </nav>

    <!-- CONTENT BODY -->
    <main class="max-w-7xl mx-auto w-full px-4 sm:px-8 py-8 flex-1 space-y-8">

        <!-- TAB 1: RINGKASAN & STATUS REZIM -->
        <div id="tab-overview" class="tab-pane space-y-6">
            
            {tri_asset_hub_html}
            {tri_asset_risk_table_html}
            <!-- Quantitative Macro Factor & Liquidity Bar (ML4T Bab 2 & Bab 4) -->
            <div class="finviz-card bg-white dark:bg-[#131922] p-5 rounded-lg border border-slate-200 dark:border-[#1f2937] shadow-sm">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-200 dark:border-[#1f2937] gap-2">
                    <div>
                        <div class="text-[11px] font-mono font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                            <span>Likuiditas & Indikator Kuantitatif Lintas Makro (Point-in-Time)</span>
                        </div>
                        <h3 class="text-sm sm:text-base font-extrabold uppercase font-mono text-slate-900 dark:text-white mt-0.5">
                            Pilar Likuiditas The Fed, Kurva Yield & Tekanan Volatilitas
                        </h3>
                    </div>
                    <div class="flex items-center gap-2 font-mono text-xs">
                        <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-slate-100 dark:bg-[#161d27] border border-slate-300 dark:border-[#232e3d] text-slate-700 dark:text-slate-300">
                            EWS: {regime['score_bahaya']} Bahaya / {regime['score_waspada']} Waspada
                        </span>
                    </div>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-3 text-xs font-mono">
                    <div class="p-3 rounded bg-slate-50 dark:bg-[#17202c] border border-slate-200 dark:border-[#233042]">
                        <div class="text-[10px] text-slate-500 dark:text-slate-400">Likuiditas Bersih Fed</div>
                        <div class="text-sm font-bold text-slate-900 dark:text-white mt-1">${net_liq.get('net_liquidity_bil', 0):,.1f}B</div>
                        <div class="text-[10px] text-slate-500 mt-0.5">4W: {chg_liq_str}</div>
                    </div>

                    <div class="p-3 rounded bg-slate-50 dark:bg-[#17202c] border border-slate-200 dark:border-[#233042]">
                        <div class="text-[10px] text-slate-500 dark:text-slate-400">Slope Kurva (10Y-3M)</div>
                        <div class="text-sm font-bold text-slate-900 dark:text-white mt-1">{(prices.get('^TNX', {}).get('close', 0) - prices.get('^IRX', {}).get('close', 0)):+.2f}%</div>
                        <div class="text-[10px] text-blue-500 mt-0.5">10Y: {prices.get('^TNX', {}).get('close', 0):.2f}%</div>
                    </div>

                    <div class="p-3 rounded bg-slate-50 dark:bg-[#17202c] border border-slate-200 dark:border-[#233042]">
                        <div class="text-[10px] text-slate-500 dark:text-slate-400">Spread BI - Fed</div>
                        <div class="text-sm font-bold text-slate-900 dark:text-white mt-1">+1.12%</div>
                        <div class="text-[10px] text-amber-500 mt-0.5">Penyempitan Spread</div>
                    </div>

                    <div class="p-3 rounded bg-slate-50 dark:bg-[#17202c] border border-slate-200 dark:border-[#233042]">
                        <div class="text-[10px] text-slate-500 dark:text-slate-400">Minyak Mentah WTI</div>
                        <div class="text-sm font-bold text-slate-900 dark:text-white mt-1">${prices.get('CL=F', {}).get('close', 0):.2f}</div>
                        <div class="text-[10px] text-slate-500 mt-0.5">1D: {prices.get('CL=F', {}).get('change_1d_pct', 0):+.2f}%</div>
                    </div>

                    <div class="p-3 rounded bg-slate-50 dark:bg-[#17202c] border border-slate-200 dark:border-[#233042]">
                        <div class="text-[10px] text-slate-500 dark:text-slate-400">Indeks DXY & Kurs</div>
                        <div class="text-sm font-bold text-slate-900 dark:text-white mt-1">{prices.get('DX-Y.NYB', {}).get('close', 0):.2f}</div>
                        <div class="text-[10px] text-rose-500 mt-0.5">USD/IDR Rp {indo_macro['usdidr_val']:,.0f}</div>
                    </div>

                    <div class="p-3 rounded bg-slate-50 dark:bg-[#17202c] border border-slate-200 dark:border-[#233042]">
                        <div class="text-[10px] text-slate-500 dark:text-slate-400">CBOE Volatilitas VIX</div>
                        <div class="text-sm font-bold text-slate-900 dark:text-white mt-1">{prices.get('^VIX', {}).get('close', 0):.2f}</div>
                        <div class="text-[10px] text-emerald-500 mt-0.5">Zona Normal (&lt;22)</div>
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

        {curriculum_tab_html}

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
                        <p class="text-[11px] text-stone-500 mt-0.5">Probabilitas skenario makro diturunkan dari probabilitas kuadran makro multi-faktor (Stagflasi vs Disinflasi vs Kontraksi), premi risiko komoditas minyak WTI, dan indikator likuiditas The Fed.</p>
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

                        <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
                            <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                                <div class="text-[10px] uppercase font-bold text-stone-500">Konsensus Pasar</div>
                                <div class="font-mono text-stone-800">Sebelum: {ev['prev']}</div>
                                <div class="font-mono font-bold text-forest-800">Ekspektasi: {ev['cons']}</div>
                                <div class="text-[9px] text-stone-500 font-mono">({ev.get('cons_source', 'Konsensus')})</div>
                            </div>
                            <div class="p-3 bg-linen-100 rounded-xl border border-linen-300 space-y-1">
                                <div class="text-[10px] uppercase font-bold text-forest-900">Rilis Data Aktual</div>
                                <div class="font-mono font-extrabold text-forest-900">Aktual: {ev.get('actual', '-')}</div>
                                <div class="font-mono font-semibold text-stone-600">Kejutan: {ev.get('surprise', '-')}</div>
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
                        <p class="text-xs sm:text-sm text-stone-600">Diurutkan berdasarkan skor momentum terbobot multi-horizon (1D 20%, 5D 30%, 20D 50%) dan overlay keselarasan siklus makro</p>
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
                    <b>Metodologi Scorecard & Alokasi:</b> Skor dihitung murni dari momentum harga (bobot: 1D 20%, 5D 30%, 20D 50%). Rekomendasi alokasi (Overweight, Underweight, Netral) menggabungkan skor momentum dengan klasifikasi sektor unggulan dan tertinggal dari rezim makro aktif. Hanya sektor utilitas, konsumer primer, dan kesehatan (XLU, XLP, XLV) yang dikategorikan defensif.
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
                            {f"{indo_macro['ihsg_val']:,.2f}" if indo_macro.get('ihsg_val') else "N/A"}
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
                        <div class="text-xs text-stone-600 font-semibold">{indo_macro.get('eido_status', 'N/A')}</div>
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
                        <div class="font-bold text-forest-800">2. Jalur Emas Spot ({f"${prices['GC=F']['close']:,.1f}" if prices.get('GC=F', {}).get('close') else "N/A"}/oz)</div>
                        <p class="text-stone-600 leading-relaxed">Emas bertahan di area elevasi tinggi mencerminkan peran aset jangkar lindung nilai geopolitik dan diversifikasi cadangan devisa global.</p>
                    </div>
                    <div class="p-3 bg-white rounded-xl border border-linen-200 space-y-1">
                        <div class="font-bold text-forest-800">3. Dampak Indonesia (USD/IDR & APBN)</div>
                        <p class="text-stone-600 leading-relaxed">Beban subsidi migas meningkat dan Bank Indonesia mengoptimalkan intervensi valas (DNDF dan pasar spot) guna menjaga stabilitas nilai tukar Rupiah.</p>
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
                        <span class="text-stone-600">Jadwal Kalender Terkonversi DST (WIB) &bull; Dinamika Pasar & Sentimen Terkalibrasi &bull; Feed Disinkronkan</span>
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
                <div><b class="text-white">Sumber Data Pasar & Neraca:</b> Yahoo Finance (US Equities, Yields, Commodities), FRED (Federal Reserve St. Louis), FXRatesAPI (London Spot Gold), Binance API</div>
                <div class="text-[11px] text-sage-300"><b class="text-sprout">Sumber Berita Makro Hari Ini:</b> {active_news_sources_str}</div>
            </div>
            <div class="text-xs text-sage-300 font-mono">
                Pembaruan: <span class="text-sprout">{display_date}</span>
            </div>
        </div>
    </footer>

    <!-- JAVASCRIPT: TAB SWITCHER, DUAL CLOCK, LIVE CRYPTO POLLING, DYNAMIC LANDSCAPE -->
    <script>
        // 7. Finviz Dark / Light Mode Switcher
        function toggleFinvizTheme() {{
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('finviz_theme', isDark ? 'dark' : 'light');
            updateThemeToggleUI(isDark);
        }}

        function updateThemeToggleUI(isDark) {{
            const icon = document.getElementById('theme-icon');
            const label = document.getElementById('theme-label');
            const btn = document.getElementById('theme-toggle');
            if (icon) icon.textContent = isDark ? '🌙' : '☀️';
            if (label) label.textContent = isDark ? 'DARK' : 'LIGHT';
            if (btn) {{
                if (isDark) {{
                    btn.className = 'flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono font-bold transition-all border border-[#2a384c] bg-[#161d27] text-slate-200 hover:bg-[#1e2736] hover:text-white cursor-pointer shadow-sm';
                }} else {{
                    btn.className = 'flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono font-bold transition-all border border-slate-300 bg-slate-100 text-slate-800 hover:bg-slate-200 cursor-pointer shadow-sm';
                }}
            }}
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            const isDark = document.documentElement.classList.contains('dark');
            updateThemeToggleUI(isDark);
        }});

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
