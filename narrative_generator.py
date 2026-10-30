"""
Narrative & Causality Chain Generator
Generates:
1. Copy-paste ready WhatsApp / Telegram Macro & Sector Impact Broadcast
2. Executive Summary and Causality Narrative for the HTML Dashboard
"""

import datetime

WIB_TZ = datetime.timezone(datetime.timedelta(hours=7))

def get_wib_now():
    return datetime.datetime.now(WIB_TZ)

def generate_whatsapp_broadcast(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio, indo_macro=None, weekly_calendar=None, flow_proj=None):
    now_str = get_wib_now().strftime("%A, %d %b %Y · %H:%M WIB")
    prices = snapshot.get("prices", {})
    net_liq = snapshot.get("net_liquidity", {})
    
    # Key Price Numbers
    spx = prices.get("SPY", {}).get("close", 0)
    spx_chg = prices.get("SPY", {}).get("change_1d_pct", 0)
    qqq = prices.get("QQQ", {}).get("close", 0)
    qqq_chg = prices.get("QQQ", {}).get("change_1d_pct", 0)
    btc = prices.get("BTC-USD", {}).get("close", 0)
    btc_chg = prices.get("BTC-USD", {}).get("change_1d_pct", 0)
    us10y = prices.get("^TNX", {}).get("close", 0)
    vix = prices.get("^VIX", {}).get("close", 0)
    oil = prices.get("CL=F", {}).get("close", 0)
    oil_chg = prices.get("CL=F", {}).get("change_1d_pct", 0)
    gold = prices.get("GC=F", {}).get("close", 0)
    gold_chg = prices.get("GC=F", {}).get("change_1d_pct", 0)
    dxy = prices.get("DX-Y.NYB", {}).get("close", 0)
    usdidr = prices.get("USDIDR=X", {}).get("close", 18100)
    usdidr_chg = prices.get("USDIDR=X", {}).get("change_1d_pct", 0)
    eido = prices.get("EIDO", {}).get("close", 10.45)
    eido_chg = prices.get("EIDO", {}).get("change_1d_pct", 0)
    
    # Net Liquidity
    net_liq_val = net_liq.get("net_liquidity_bil", 0)
    net_liq_chg = net_liq.get("change_4w_bil", 0)
    
    # EWS counts
    bahaya_count = sum(1 for s in ews_signals if s["status"] == "BAHAYA")
    waspada_count = sum(1 for s in ews_signals if s["status"] == "WASPADA")
    aman_count = sum(1 for s in ews_signals if s["status"] == "AMAN")
    
    # Sector Leaders & Laggards
    top_3 = sectors[:3]
    bottom_3 = sectors[-3:]
    
    # Dynamic Causality Chain based on Regime
    if regime["regime_id"] == "STAGFLASI":
        chain_1 = f"Minyak WTI (${oil:.2f}) & US10Y ({us10y:.2f}%) berada di zona elevasi tinggi"
        chain_2 = "Ekspektasi Inflasi bertahan alot -> The Fed terkunci pada suku bunga tinggi (Higher for Longer)"
        chain_3 = "Suku Bunga Riil (TIPS) menekan valuasi PE saham High-Beta Tech & menahan inflow Crypto"
        chain_4 = "Terjadi rotasi modal agresif ke sektor Energi (XLE) & Material (XLB) sebagai benteng proteksi inflasi"
    elif regime["regime_id"] == "DISINFLASI_BOOM":
        chain_1 = f"Fed Net Liquidity berekspansi (+${net_liq_chg:.1f}B 4W) di tengah VIX rendah ({vix:.1f})"
        chain_2 = "Pelunakan inflasi membuka ruang ekspansi valuasi -> Discount rate obligasi stabil"
        chain_3 = "Likuiditas sistem mengalir deras ke aset berbasis durasi panjang & high convexity"
        chain_4 = "Sektor Teknologi (XLK), Komunikasi (XLC), dan Bitcoin (BTC) memimpin reli pasar"
    elif regime["regime_id"] == "REFLASI":
        chain_1 = f"Pertumbuhan ekonomi resilien + Komoditas menguat (Minyak ${oil:.2f})"
        chain_2 = "Kurva yield mengalami steepening -> Margin bunga perbankan membaik"
        chain_3 = "Rotasi beralih dari defensif ke emiten siklikal & perbankan"
        chain_4 = "Finansial (XLF) dan Industri (XLI) outperform; BTC selektif mengikuti risk appetite"
    else:
        chain_1 = f"Tekanan likuiditas & VIX naik ({vix:.1f}) dengan spread obligasi sampah melebar"
        chain_2 = "Kekhawatiran penurunan laba korporasi (Earnings contraction)"
        chain_3 = "De-risking portofolio institusi global -> Flight to Quality & Cash"
        chain_4 = "Utilitas (XLU) dan Kesehatan (XLV) defensif; Crypto mengalami kompresi volatilitas"

    # Indonesia block text
    indo_block = ""
    if indo_macro:
        indo_block = f"""
━━━━━━━━━━━━━━━━━━━━━
🇮🇩 *TRANSMISI MAKRO GLOBAL KE INDONESIA:*
• *USD / IDR (Kurs):* Rp {usdidr:,.0f} ({usdidr_chg:+.2f}%) [{indo_macro['kurs_status']}]
• *MSCI Indonesia (EIDO):* ${eido:.2f} ({eido_chg:+.2f}%) [{indo_macro['ihsg_status']}]
• *Kebijakan Bank Indonesia:* {indo_macro['bi_status']}
• *Beban APBN & Subsidi:* {indo_macro['apbn_status']}
• *Analisis:* {indo_macro['summary']}
"""

    # Weekly Calendar block text
    cal_block = ""
    if weekly_calendar:
        top_events = weekly_calendar[:3]
        cal_items = []
        for e in top_events:
            cal_items.append(f"• *{e['date']} {e['time_wib']}* [{e['country']}]: {e['event']} ({e['importance']})\n  ↳ *Dampak Hot:* {e['impact_hot']}\n  ↳ *Aset Pilihan:* {e['favored_asset']}")
        cal_block = f"""
━━━━━━━━━━━━━━━━━━━━━
📅 *KATALIS KALENDER EKONOMI PEKAN INI & DAMPAK:*
{chr(10).join(cal_items)}
"""

    # Flow Projection block text
    flow_block = ""
    if flow_proj:
        scen_a = flow_proj["scenarios"][0]
        flow_block = f"""
━━━━━━━━━━━━━━━━━━━━━
🌊 *FLOW PROJECTION (ARUS LIKUIDITAS & MODAL):*
• *Arah Arus Modal Masuk:* {', '.join([i['asset'] for i in flow_proj['inflows'][:2]])}
• *Sumber Penarikan Likuiditas:* {', '.join([d['asset'] for d in flow_proj['drainages'][:2]])}
• *Proyeksi Utama ({scen_a['name']} - Prob {scen_a['prob']}):*
  ↳ *Sektor US:* {scen_a['us_sectors_path']}
  ↳ *Crypto:* {scen_a['crypto_path']}
  ↳ *Indonesia:* {scen_a['indonesia_path']}
"""

    msg = f"""🌐 *MACRO PULSE | US SECTORS, CRYPTO & INDONESIA*
📅 {now_str}
🏛 *REZIM MAKRO:* {regime['title']}
⚠️ *STATUS EWS:* 🔴 {bahaya_count} Bahaya | 🟡 {waspada_count} Waspada | 🟢 {aman_count} Aman

━━━━━━━━━━━━━━━━━━━━━
⚡ *RANTAI TRANSMISI KAUSALITAS (SENTIMEN & DAMPAK):*
1️⃣ *Pemicu:* {chain_1}
   ⬇️
2️⃣ *Transmisi Moneter:* {chain_2}
   ⬇️
3️⃣ *Efek Likuiditas:* {chain_3}
   ⬇️
4️⃣ *Dampak Akhir Sektor & Crypto:* {chain_4}

━━━━━━━━━━━━━━━━━━━━━
📊 *MARKET SNAPSHOT:*
• *S&P 500 (SPY):* ${spx:.2f} ({spx_chg:+.2f}%)
• *Nasdaq (QQQ):* ${qqq:.2f} ({qqq_chg:+.2f}%)
• *Bitcoin (BTC):* ${btc:,.0f} ({btc_chg:+.2f}%)
• *Emas (XAUUSD):* ${gold:,.1f}/oz ({gold_chg:+.2f}%)
• *USD / IDR:* Rp {usdidr:,.0f} ({usdidr_chg:+.2f}%)
• *US 10Y Yield:* {us10y:.3f}%
• *DXY (Dollar):* {dxy:.2f}
• *WTI Oil:* ${oil:.2f} ({oil_chg:+.2f}%)
• *Fed Net Liquidity:* ${net_liq_val:,.1f}B ({net_liq_chg:+.1f}B 4W)
{indo_block}{cal_block}{flow_block}
━━━━━━━━━━━━━━━━━━━━━
🏆 *ROTASI 11 SEKTOR US (TACTICAL ACTION):*
🟢 *Top Momentum (Overweight):*
{chr(10).join([f"  • *{s['ticker']}* ({s['name']}): Momentum Score {s['momentum_score']:+.1f} | 1D: {s['chg_1d']:+.2f}% | 20D: {s['chg_20d']:+.2f}%" for s in top_3])}

🔴 *Bottom Laggards (Underweight):*
{chr(10).join([f"  • *{s['ticker']}* ({s['name']}): Momentum Score {s['momentum_score']:+.1f} | 1D: {s['chg_1d']:+.2f}% | 20D: {s['chg_20d']:+.2f}%" for s in bottom_3])}

━━━━━━━━━━━━━━━━━━━━━
🪙 *CRYPTO & LIQUIDITY MATRIX:*
• *BTC-USD:* ${btc:,.0f} (20D Chg: {prices.get('BTC-USD', {}).get('change_20d_pct', 0):+.2f}%)
• *ETH-USD:* ${prices.get('ETH-USD', {}).get('close', 0):,.0f}
• *SOL-USD:* ${prices.get('SOL-USD', {}).get('close', 0):,.2f}
• *ETH/BTC Ratio:* {eth_btc_ratio:.4f} {'(Altseason Pause / BTC Dominance)' if eth_btc_ratio < 0.05 else '(Altcoins Risk-On)'}
• *Crypto Stance:* {regime['crypto_stance']}

━━━━━━━━━━━━━━━━━━━━━
💡 *KESIMPULAN & STRATEGI EKSEKUSI:*
{regime['summary']}
• *Historical Analog:* Mirip episode _{regime['analog']}_.
• *Playbook:* Fokus alokasi pada sektor yang selaras dengan siklus saat ini ({', '.join(regime['favored_sectors'])}). Hindari agresivitas di sektor tertinggal ({', '.join(regime['lagging_sectors'])}).

_Generated by Antigravity US Macro & Crypto Engine_"""
    return msg.strip()

def generate_report_payload(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio, indo_macro=None, weekly_calendar=None, flow_proj=None, market_drivers=None):
    whatsapp_text = generate_whatsapp_broadcast(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio, indo_macro, weekly_calendar, flow_proj)
    wib_now = get_wib_now()
    
    payload = {
        "timestamp": wib_now.strftime("%Y-%m-%d %H:%M:%S"),
        "display_date": wib_now.strftime("%A, %d %B %Y · %H:%M WIB"),
        "iso_timestamp": wib_now.isoformat(),
        "regime": regime,
        "ews": ews_signals,
        "correlations": corrs,
        "sectors": sectors,
        "crypto": crypto_data,
        "eth_btc_ratio": eth_btc_ratio,
        "net_liquidity": snapshot.get("net_liquidity", {}),
        "macro_prices": snapshot.get("prices", {}),
        "global_news": snapshot.get("global_news", []),
        "geopolitics_news": snapshot.get("geopolitics_news", []),
        "crypto_news": snapshot.get("crypto_news", []),
        "indonesia_news": snapshot.get("indonesia_news", []),
        "indo_macro": indo_macro,
        "weekly_calendar": weekly_calendar or [],
        "flow_proj": flow_proj or {},
        "market_drivers": market_drivers or {},
        "whatsapp_broadcast": whatsapp_text
    }
    return payload
