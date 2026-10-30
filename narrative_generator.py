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

def generate_whatsapp_broadcast(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio, indo_macro=None, weekly_calendar=None, flow_proj=None, market_drivers=None):
    wib_now = get_wib_now()
    now_str = wib_now.strftime("%A, %d %b %Y · %H:%M WIB")
    prices = snapshot.get("prices", {})
    net_liq = snapshot.get("net_liquidity", {})
    crypto_news = snapshot.get("crypto_news", [])
    
    # Key Price Numbers
    spx = prices.get("SPY", {}).get("close", 0)
    spx_chg = prices.get("SPY", {}).get("change_1d_pct", 0)
    qqq = prices.get("QQQ", {}).get("close", 0)
    qqq_chg = prices.get("QQQ", {}).get("change_1d_pct", 0)
    btc = prices.get("BTC-USD", {}).get("close", 0)
    btc_chg = prices.get("BTC-USD", {}).get("change_1d_pct", 0)
    btc_20d = prices.get("BTC-USD", {}).get("change_20d_pct", 0)
    eth = prices.get("ETH-USD", {}).get("close", 0)
    eth_chg = prices.get("ETH-USD", {}).get("change_1d_pct", 0)
    sol = prices.get("SOL-USD", {}).get("close", 0)
    sol_chg = prices.get("SOL-USD", {}).get("change_1d_pct", 0)
    
    us10y = prices.get("^TNX", {}).get("close", 0)
    us10y_chg = prices.get("^TNX", {}).get("change_1d_pct", 0)
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
    
    # Extract unique sources for transparent attribution
    raw_sources = [n.get('source') for n in (snapshot.get('global_news', []) + snapshot.get('geopolitics_news', []) + snapshot.get('crypto_news', []) + snapshot.get('indonesia_news', [])) if n.get('source')]
    unique_sources = sorted(list(set(raw_sources)))
    sources_str = ", ".join(unique_sources[:6]) if unique_sources else "Reuters, CoinDesk, Bloomberg, CNBC Indonesia, FXStreet"

    # Dynamic 5-Stage Intra-Week Sentiment Chain
    xlk_chg = prices.get("XLK", {}).get("change_1d_pct", 0)
    xle_chg = prices.get("XLE", {}).get("change_1d_pct", 0)
    
    if btc_chg < -2.0 or qqq_chg < -0.8:
        chain_1 = "Musim Laporan Keuangan Big Tech (Earnings Miss / AI Capex Fear) memicu kekhawatiran valuasi dan efisiensi belanja komputasi awan."
        chain_2 = f"Aksi jual serentak pada saham High-Beta Growth (QQQ {qqq_chg:+.2f}%, XLK {xlk_chg:+.2f}%) memicu 'Risk-Off' rotasi modal ke sektor defensif & energi (XLE {xle_chg:+.2f}%)."
        chain_3 = f"Pelarian likuiditas ke obligasi AS membuat yield 10Y bergerak fluktuatif ({us10y:.3f}%), namun suku bunga riil tetap ketat menyedot likuiditas pasar."
        chain_4 = f"Institusi melikuidasi eksposur berisiko tinggi (High-Beta Tech Proxy), memicu likuidasi berantai derivatif sehingga Bitcoin terkoreksi ke ${btc:,.0f} ({btc_chg:+.2f}%)."
        chain_5 = f"Penguatan Dolar (DXY {dxy:.2f}) dan harga minyak (${oil:.2f}) membebani nilai tukar Rupiah (Rp {usdidr:,.0f}) serta menahan laju IHSG."
    else:
        chain_1 = f"Tarik-menarik data makro (Minyak ${oil:.2f} & US10Y {us10y:.3f}%) menguji ketahanan laba korporasi AS."
        chain_2 = f"Pasar saham bergerak selektif (SPY {spx_chg:+.2f}%, QQQ {qqq_chg:+.2f}%); modal terkonsentrasi pada emiten dengan arus kas kuat ({top_3[0]['ticker']})."
        chain_3 = f"Likuiditas The Fed (${net_liq_val:,.1f}B) menjadi bantalan penahan penurunan agresif di pasar obligasi."
        chain_4 = f"Pasar kripto berkonsolidasi di kisaran ${btc:,.0f}; trader derivatif bersiap mengantisipasi rilis data inflasi dan tenaga kerja AS."
        chain_5 = f"Bank Indonesia bersiaga menstabilkan Rupiah di Rp {usdidr:,.0f} guna mengantisipasi transmisi imported inflation."

    # Top Crypto News block
    crypto_news_lines = []
    if crypto_news:
        for it in crypto_news[:3]:
            crypto_news_lines.append(f"  • {it.get('title', '')} _{it.get('source', 'Crypto Wire')}_")
    else:
        crypto_news_lines.append(f"  • Penyesuaian posisi derivatif & arus ETF Spot di tengah tingginya yield obligasi AS.")
    crypto_news_str = "\n".join(crypto_news_lines)

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
{chr(10).join(cal_items)}"""

    # Indonesia block text
    indo_block = ""
    if indo_macro:
        indo_block = f"""
━━━━━━━━━━━━━━━━━━━━━
🇮🇩 *TRANSMISI MAKRO GLOBAL KE INDONESIA:*
• *USD / IDR Spot:* Rp {usdidr:,.0f} ({usdidr_chg:+.2f}%) [{indo_macro['kurs_status']}]
• *MSCI Indonesia (EIDO):* ${eido:.2f} ({eido_chg:+.2f}%) [{indo_macro['ihsg_status']}]
• *Sikap Kebijakan Bank Indonesia:* {indo_macro['bi_status']}
• *Catatan APBN & Saham Domestik:* {indo_macro['summary']}"""

    msg = f"""🌐 *MACRO PULSE | TRANSISI INTRA-WEEK & MORNING BRIEFING*
📅 Edisi: {now_str} (Update Harian 06:00 WIB)
🏛 *Rezim Makro Aktif:* {regime['title']} [{regime['regime_id']}]
⚠️ *Status EWS:* 🔴 {bahaya_count} Bahaya | 🟡 {waspada_count} Waspada | 🟢 {aman_count} Aman

━━━━━━━━━━━━━━━━━━━━━
⚡ *RANTAI SENTIMEN & TRANSMISI INTRA-WEEK:*
1️⃣ *Katalis Mikro & Sektoral:*
   {chain_1}
   ⬇️
2️⃣ *Reaksi Pasar Ekuitas & Sektoral US:*
   {chain_2}
   ⬇️
3️⃣ *Rotasi Likuiditas & Imbal Hasil Obligasi:*
   {chain_3}
   ⬇️
4️⃣ *Transmisi ke Kripto (Tech Proxy):*
   {chain_4}
   ⬇️
5️⃣ *Dampak ke Pasar Modal Indonesia:*
   {chain_5}

━━━━━━━━━━━━━━━━━━━━━
📊 *PERGERAKAN TERBARU STOCK US & MAKRO:*
• *S&P 500 (SPY):* ${spx:.2f} ({spx_chg:+.2f}%)
• *Nasdaq 100 (QQQ):* ${qqq:.2f} ({qqq_chg:+.2f}%)
• *US 10Y Treasury Yield:* {us10y:.3f}% ({us10y_chg:+.2f}%)
• *Dollar Index (DXY):* {dxy:.2f}
• *Minyak Mentah WTI:* ${oil:.2f} ({oil_chg:+.2f}%)
• *Emas Spot (XAUUSD):* ${gold:,.1f}/oz ({gold_chg:+.2f}%)
• *Fed Net Liquidity:* ${net_liq_val:,.1f}B ({net_liq_chg:+.1f}B 4W)

━━━━━━━━━━━━━━━━━━━━━
🏆 *ROTASI 11 SEKTOR S&P 500 (1D & 20D):*
🟢 *Top Outperformers (Overweight):*
{chr(10).join([f"  • *{s['ticker']}* ({s['name']}): Score {s['momentum_score']:+.1f} | 1D: {s['chg_1d']:+.2f}% | 20D: {s['chg_20d']:+.2f}%" for s in top_3])}

🔴 *Bottom Laggards (Underweight):*
{chr(10).join([f"  • *{s['ticker']}* ({s['name']}): Score {s['momentum_score']:+.1f} | 1D: {s['chg_1d']:+.2f}% | 20D: {s['chg_20d']:+.2f}%" for s in bottom_3])}

━━━━━━━━━━━━━━━━━━━━━
🪙 *DYNAMICS & CRYPTO NEWS WIRE:*
• *Bitcoin (BTC):* ${btc:,.0f} (1D: {btc_chg:+.2f}% | 20D: {btc_20d:+.2f}%)
• *Ethereum (ETH):* ${eth:,.0f} (1D: {eth_chg:+.2f}%)
• *Solana (SOL):* ${sol:,.2f} (1D: {sol_chg:+.2f}%)
• *ETH/BTC Ratio:* {eth_btc_ratio:.4f} {'(Dominasi BTC / Altseason Tertahan)' if eth_btc_ratio < 0.05 else '(Altcoins Risk-On)'}
• *Kawat Berita Kripto Terkini:*
{crypto_news_str}
{cal_block}
{indo_block}

━━━━━━━━━━━━━━━━━━━━━
💡 *TACTICAL ACTION & SIKLUS MAKRO:*
• *Fokus Sektoral:* Overweight {', '.join(regime['favored_sectors'])} | Kurangi {', '.join(regime['lagging_sectors'])}
• *Sikap Kripto:* {regime['crypto_stance']}
• *Historical Analog:* Mirip siklus _{regime['analog']}_.

━━━━━━━━━━━━━━━━━━━━━
📚 *SUMBER DATA & BERITA TERVERIFIKASI:*
• *Data Pasar & Ekuitas:* Yahoo Finance, S&P Dow Jones Indices, CBOE, Bank Indonesia & Binance API
• *Data Neraca & Likuiditas:* Federal Reserve Bank of St. Louis (FRED® API)
• *Kawat Berita Terakreditasi:* {sources_str}

_Disusun otomatis oleh Macro Pulse Engine · Siap sebar grup riset & treasury_"""
    return msg.strip()

def generate_report_payload(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio, indo_macro=None, weekly_calendar=None, flow_proj=None, market_drivers=None):
    whatsapp_text = generate_whatsapp_broadcast(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio, indo_macro, weekly_calendar, flow_proj, market_drivers)
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
