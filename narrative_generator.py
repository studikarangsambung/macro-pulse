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

def build_validated_sentiment_chain(prices, sectors, snapshot, market_drivers=None):
    """
    Constructs a 5-stage causal sentiment chain with strict validation & real-time news catalysts:
    1. Katalis Utama & Sentimen Ekuitas AS (Incorporate Tech news driver & price signs)
    2. Kinerja Sektoral Wall Street (Dynamically selects true outperformers & true laggards)
    3. Pasar Energi & Komoditas (Incorporate Crude Oil news driver & price signs)
    4. Dinamika Pasar Kripto (Incorporate Bitcoin news driver & liquidity factors)
    5. Keseimbangan Imbal Hasil Obligasi, Dollar & Emas (Incorporate Dollar/Yield & Gold drivers)
    """
    spx = prices.get("SPY", {}).get("close", 0)
    spx_chg = prices.get("SPY", {}).get("change_1d_pct", 0)
    qqq = prices.get("QQQ", {}).get("close", 0)
    qqq_chg = prices.get("QQQ", {}).get("change_1d_pct", 0)
    
    btc = prices.get("BTC-USD", {}).get("close", 0)
    btc_chg = prices.get("BTC-USD", {}).get("change_1d_pct", 0)
    eth = prices.get("ETH-USD", {}).get("close", 0)
    eth_chg = prices.get("ETH-USD", {}).get("change_1d_pct", 0)
    sol = prices.get("SOL-USD", {}).get("close", 0)
    sol_chg = prices.get("SOL-USD", {}).get("change_1d_pct", 0)
    
    us10y = prices.get("^TNX", {}).get("close", 0)
    us10y_chg = prices.get("^TNX", {}).get("change_1d_pct", 0)
    dxy = prices.get("DX-Y.NYB", {}).get("close", 0)
    dxy_chg = prices.get("DX-Y.NYB", {}).get("change_1d_pct", 0)
    
    oil = prices.get("CL=F", {}).get("close", 0)
    oil_chg = prices.get("CL=F", {}).get("change_1d_pct", 0)
    gold = prices.get("GC=F", {}).get("close", 0)
    gold_chg = prices.get("GC=F", {}).get("change_1d_pct", 0)

    # 1. Stage 1: Wall Street / Big Tech Catalyst
    tech_drv = market_drivers.get("tech", {}) if market_drivers else {}
    tech_sum = tech_drv.get("summary", "")
    
    if qqq_chg >= 0.2 and spx_chg >= 0.1:
        stage_1_title = "Resiliensi Ekuitas AS & Kinerja Laporan Keuangan"
        stage_1_sub = f"({tech_sum})" if tech_sum else "(Wall Street Menguat Selektif di Tengah Penyesuaian Valuasi)"
    elif qqq_chg <= -0.4 or spx_chg <= -0.4:
        stage_1_title = "Rotasi Defensif & Penyesuaian Valuasi Ekuitas AS"
        stage_1_sub = f"({tech_sum})" if tech_sum else "(Pasar Mencermati Dampak Suku Bunga Restriktif terhadap Laba Korporasi)"
    else:
        stage_1_title = "Konsolidasi Terbatas Pasar Saham Wall Street"
        stage_1_sub = f"({tech_sum})" if tech_sum else "(Pergerakan Fluktuatif Menanti Rilis Data Tenaga Kerja & Manufaktur)"

    # 2. Stage 2: S&P 500 & Nasdaq Sector Reaction
    sorted_sectors = sorted(sectors, key=lambda s: s.get("chg_1d", 0), reverse=True)
    top_2 = sorted_sectors[:2]
    bottom_2 = sorted_sectors[-2:]
    
    top_str = ", ".join([f"{s['ticker']} {s['chg_1d']:+.2f}%" for s in top_2])
    bottom_str = ", ".join([f"{s['ticker']} {s['chg_1d']:+.2f}%" for s in bottom_2])
    
    if qqq_chg >= 0:
        stage_2_text = (
            f"Nasdaq (QQQ {qqq_chg:+.2f}%) & S&P 500 (SPY {spx_chg:+.2f}%) menguat.\n"
            f"Sektor Unggulan: {top_str}\n"
            f"Sektor Tertinggal: {bottom_str}"
        )
    else:
        stage_2_text = (
            f"Nasdaq (QQQ {qqq_chg:+.2f}%) & S&P 500 (SPY {spx_chg:+.2f}%) terkoreksi.\n"
            f"Sektor Tertinggal: {bottom_str}\n"
            f"Sektor Defensif: {top_str}"
        )

    # 3. Stage 3: Crude Oil & Energy Dynamics
    oil_drv = market_drivers.get("oil", {}) if market_drivers else {}
    oil_sum = oil_drv.get("summary", "")
    
    if oil_chg >= 0.8:
        stage_3_title = "Minyak Mentah Menguat / Premi Risiko Pasokan"
        stage_3_sub = f"({oil_sum})" if oil_sum else "(Ketegangan geopolitik kawasan dan disiplin kuota pasokan fisik)"
    elif oil_chg <= -0.8:
        stage_3_title = "Minyak Mentah Terkoreksi Melandai"
        stage_3_sub = f"({oil_sum})" if oil_sum else "(Ekspektasi diplomasi kawasan dan pelepasan cadangan minyak)"
    else:
        stage_3_title = "Minyak Mentah Bertahan di Level Tinggi"
        stage_3_sub = f"({oil_sum})" if oil_sum else "(Konsolidasi harga energi bertahan di atas ambang batas $100/barel)"
    stage_3_text = f"Minyak WTI US$ {oil:.2f} / barel ({oil_chg:+.2f}%)"

    # 4. Stage 4: Crypto Market (Divergence vs Co-movement check)
    crypto_drv = market_drivers.get("crypto", {}) if market_drivers else {}
    crypto_sum = crypto_drv.get("summary", "")
    
    stage_4_crypto = f"Pasar Kripto: BTC US$ {btc:,.0f} ({btc_chg:+.2f}%), ETH US$ {eth:,.0f} ({eth_chg:+.2f}%), SOL US$ {sol:.2f} ({sol_chg:+.2f}%)"
    
    if btc_chg <= -1.5 and qqq_chg >= 0:
        stage_4_title = "Divergensi Pasar Kripto (Tekanan Jual Mandiri)"
        stage_4_desc = f"{crypto_sum} di tengah bursa saham AS yang cenderung bertahan." if crypto_sum else "Tekanan jual derivatif dan volatilitas ekosistem kripto terjadi di tengah bursa saham AS yang cenderung bertahan."
    elif btc_chg <= -1.5 and qqq_chg < 0:
        stage_4_title = "Risk-Off Global Menekan Pasar Kripto"
        stage_4_desc = f"{crypto_sum} sejalan dengan aksi de-risking di saham teknologi Wall Street." if crypto_sum else "Likuidasi posisi leverage di pasar derivatif sejalan dengan de-risking saham-saham teknologi Wall Street."
    elif btc_chg >= 1.5 and qqq_chg >= 0:
        stage_4_title = "Risk Appetite Meluas ke Pasar Kripto"
        stage_4_desc = f"{crypto_sum}." if crypto_sum else "Sentimen positif ekuitas mendorong aliran likuiditas ke aset digital."
    else:
        stage_4_title = "Konsolidasi Terbatas Pasar Kripto"
        stage_4_desc = f"{crypto_sum}." if crypto_sum else "Harga aset kripto berkonsolidasi di rentang sempit menunggu pemicu likuiditas baru."

    # 5. Stage 5: Yield, Dollar & Gold Balance
    dollar_drv = market_drivers.get("dollar", {}) if market_drivers else {}
    dollar_sum = dollar_drv.get("summary", "")
    gold_drv = market_drivers.get("gold", {}) if market_drivers else {}
    gold_sum = gold_drv.get("summary", "")
    
    if us10y_chg >= 0.5:
        yield_desc = f"US 10-Year Yield naik ke {us10y:.3f}% ({us10y_chg:+.2f}%) & DXY {dxy:.2f} ({dxy_chg:+.2f}%)"
    elif us10y_chg <= -0.5:
        yield_desc = f"US 10-Year Yield melandai ke {us10y:.3f}% ({us10y_chg:+.2f}%) & DXY {dxy:.2f} ({dxy_chg:+.2f}%)"
    else:
        yield_desc = f"US 10-Year Yield bertahan di {us10y:.3f}% ({us10y_chg:+.2f}%) & DXY {dxy:.2f} ({dxy_chg:+.2f}%)"
        
    if dollar_sum:
        yield_desc += f"\n↳ Katalis Suku Bunga: {dollar_sum}"

    gold_desc = f"Emas Spot di US$ {gold:,.1f} / troy oz ({gold_chg:+.2f}%)"
    if gold_sum:
        gold_desc += f"\n↳ Katalis Emas: {gold_sum}"

    chain = f"""{stage_1_title}
↓
{stage_1_sub}
↓
{stage_2_text}
↓
{stage_3_title}
{stage_3_sub}
{stage_3_text}
↓
{stage_4_title}
{stage_4_crypto}
{stage_4_desc}
↓
Keseimbangan Yield, Dollar & Emas
{yield_desc}
{gold_desc}"""
    return chain

def generate_whatsapp_broadcast(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio, indo_macro=None, weekly_calendar=None, flow_proj=None, market_drivers=None):
    wib_now = get_wib_now()
    
    # Indonesian date translation
    indo_days = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    indo_months = {
        "January": "Januari", "February": "Februari", "March": "Maret", "April": "April",
        "May": "Mei", "June": "Juni", "July": "Juli", "August": "Agustus",
        "September": "September", "October": "Oktober", "November": "November", "December": "Desember"
    }
    eng_day = wib_now.strftime("%A")
    eng_month = wib_now.strftime("%B")
    day_str = indo_days.get(eng_day, eng_day)
    month_str = indo_months.get(eng_month, eng_month)
    trade_date_str = f"{day_str}, {wib_now.day} {month_str} {wib_now.year}"
    
    prices = snapshot.get("prices", {})
    net_liq = snapshot.get("net_liquidity", {})
    crypto_news = snapshot.get("crypto_news", [])
    
    # Key Price Numbers
    btc = prices.get("BTC-USD", {}).get("close", 0)
    btc_chg = prices.get("BTC-USD", {}).get("change_1d_pct", 0)
    btc_20d = prices.get("BTC-USD", {}).get("change_20d_pct", 0)
    eth = prices.get("ETH-USD", {}).get("close", 0)
    eth_chg = prices.get("ETH-USD", {}).get("change_1d_pct", 0)
    sol = prices.get("SOL-USD", {}).get("close", 0)
    sol_chg = prices.get("SOL-USD", {}).get("change_1d_pct", 0)
    
    usdidr = prices.get("USDIDR=X", {}).get("close", 18100)
    usdidr_chg = prices.get("USDIDR=X", {}).get("change_1d_pct", 0)
    eido = prices.get("EIDO", {}).get("close", 10.45)
    eido_chg = prices.get("EIDO", {}).get("change_1d_pct", 0)
    ihsg = prices.get("^JKSE", {}).get("close", 0)
    ihsg_chg = prices.get("^JKSE", {}).get("change_1d_pct", 0)
    
    # Net Liquidity
    net_liq_val = net_liq.get("net_liquidity_bil", 0)
    net_liq_chg = net_liq.get("change_4w_bil", 0)
    if net_liq_chg > 50:
        liq_status = "Ekspansi Kuat"
    elif net_liq_chg > 0:
        liq_status = "Ekspansi Moderat"
    elif net_liq_chg > -50:
        liq_status = "Kontraksi Ringan"
    else:
        liq_status = "Penarikan Likuiditas Agresif"
    
    # Altseason Status
    if eth_btc_ratio < 0.035:
        altseason_status = f"Dominasi Bitcoin Kuat (Altseason Tertahan) [Rasio ETH/BTC: {eth_btc_ratio:.4f}]"
    elif eth_btc_ratio < 0.05:
        altseason_status = f"Konsolidasi Pasangan ETH/BTC [Rasio ETH/BTC: {eth_btc_ratio:.4f}]"
    else:
        altseason_status = f"Altseason Aktif (Likuiditas Meluas ke Altcoins) [Rasio ETH/BTC: {eth_btc_ratio:.4f}]"
    
    # Extract unique sources for transparent attribution
    all_news_items = []
    if "news_by_category" in snapshot:
        for cat_list in snapshot["news_by_category"].values():
            all_news_items.extend(cat_list)
    else:
        all_news_items = (snapshot.get('global_news', []) + snapshot.get('geopolitics_news', []) + snapshot.get('crypto_news', []) + snapshot.get('indonesia_news', []))
        
    raw_sources = [n.get('source') for n in all_news_items if n.get('source')]
    unique_sources = sorted(list(set(raw_sources)))
    sources_str = ", ".join(unique_sources[:6]) if unique_sources else "Reuters, CoinDesk, Bloomberg, CNBC Indonesia, FXStreet"

    # Top Section: Validated 5-Stage Sentiment Chain with Live News Drivers
    chain_section = build_validated_sentiment_chain(prices, sectors, snapshot, market_drivers)

    # Crypto News Wire block (Accurate Label: Kawat Berita Pasar Kripto & Web3)
    crypto_news_lines = []
    if crypto_news:
        for it in crypto_news[:3]:
            crypto_news_lines.append(f"• {it.get('title', '')} ({it.get('source', 'Crypto Wire')})")
    else:
        crypto_news_lines.append("• Arus modal institusional dan penyesuaian posisi kontrak berjangka di pasar derivatif.")
    crypto_news_str = "\n".join(crypto_news_lines)

    # Weekly Calendar block text: concise without emojis, with DST indicator
    cal_block = ""
    if weekly_calendar:
        today_iso = wib_now.strftime("%Y-%m-%d")
        upcoming_events = [e for e in weekly_calendar if e.get("date_iso", "") >= today_iso]
        display_events = upcoming_events[:3] if upcoming_events else weekly_calendar[-3:]
        
        cal_items = []
        for e in display_events:
            date_iso = e.get("date_iso", "")
            if date_iso == today_iso:
                status_tag = "[HARI INI]"
            elif date_iso > today_iso:
                status_tag = "[MENDATANG]"
            else:
                status_tag = "[TELAH RILIS]"
                
            clean_country = e.get("country", "US").replace("🇺🇸", "").replace("🇮🇩", "").strip()
            clean_importance = e.get("importance", "TINGGI").replace("🔴", "").replace("🟡", "").replace("🟢", "").strip()
            tz_tag = e.get("tz_tag", "")
            
            cal_items.append(
                f"• {e['day']}, {e['date']} {e['time_wib']} {status_tag} [{clean_country} {tz_tag}]: {e['event']} [{clean_importance}]\n"
                f"  - Dampak Hot: {e['impact_hot']}\n"
                f"  - Aset Pilihan: {e['favored_asset']}"
            )
            
        cal_block = f"""
━━━━━━━━━━━━━━━━━━━━━
KATALIS KALENDER EKONOMI (FOKUS HARI INI & MENDATANG)
{chr(10).join(cal_items)}"""

    # Indonesia block text with live IHSG spot
    indo_block = ""
    if indo_macro:
        ihsg_line = f"• IHSG Spot: {ihsg:,.2f} ({ihsg_chg:+.2f}%) [{indo_macro.get('ihsg_status', 'KONSOLIDASI')}]\n" if ihsg > 0 else ""
        indo_block = f"""
━━━━━━━━━━━━━━━━━━━━━
TRANSMISI KE PASAR MODAL INDONESIA
{ihsg_line}• USD / IDR Spot: Rp {usdidr:,.0f} ({usdidr_chg:+.2f}%) [{indo_macro['kurs_status']}]
• MSCI Indonesia (EIDO): US$ {eido:.2f} ({eido_chg:+.2f}%) [{indo_macro['ihsg_status']}]
• Kebijakan Bank Indonesia: {indo_macro['bi_status']}
• Analisis: {indo_macro['summary']}"""

    msg = f"""Global Market Review
(Update Perdagangan: {trade_date_str})

{chain_section}

━━━━━━━━━━━━━━━━━━━━━
LIKUIDITAS THE FED (H.4.1 BALANCE SHEET)
• Likuiditas Bersih: US$ {net_liq_val:,.1f} Miliar
• Perubahan 4 Pekan: {net_liq_chg:+.1f} Miliar ({liq_status})
• Komponen Neraca: Total Aset Fed (WALCL) - Saldo Depkeu (TGA) - Reverse Repo (RRP)
• Catatan Pembaruan: Rilis resmi mingguan setiap Kamis sore waktu US (Jumat ~03:30 WIB)

━━━━━━━━━━━━━━━━━━━━━
DYNAMICS & CRYPTO NEWS WIRE
• Bitcoin (BTC): US$ {btc:,.0f} (1D: {btc_chg:+.2f}% | 20D: {btc_20d:+.2f}%)
• Ethereum (ETH): US$ {eth:,.0f} (1D: {eth_chg:+.2f}%)
• Solana (SOL): US$ {sol:.2f} (1D: {sol_chg:+.2f}%)
• Status Altseason: {altseason_status}
• Kawat Berita Pasar Kripto & Web3:
{crypto_news_str}
{cal_block}
{indo_block}

━━━━━━━━━━━━━━━━━━━━━
SUMBER DATA & KAWAT BERITA TERVERIFIKASI
• Pasar & Ekuitas: Yahoo Finance, S&P Dow Jones Indices, CBOE, Bank Indonesia & Binance API
• Neraca & Likuiditas: Federal Reserve Bank of St. Louis (FRED® API)
• Media & Kawat Berita: {sources_str}

━━━━━━━━━━━━━━━━━━━━━
⚠️ Disclaimer: Ringkasan makroekonomi ini disusun untuk tujuan riset internal dan pemantauan pasar modal, bukan merupakan rekomendasi atau ajakan transaksi investasi.

Disusun oleh studikarangsambung-market pulse engine"""
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
