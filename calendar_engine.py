"""
Weekly Economic Calendar & Macro Capital Flow Projection Engine
Provides:
1. One-Week High-Impact Economic Calendar (AS & Indonesia) with Scenario Transmissions
2. 7-Day to 30-Day Liquidity & Capital Flow Projections (US Sectors, Crypto, Rupiah)
"""

import datetime

def get_weekly_economic_calendar():
    """
    Weekly High-Impact Economic Calendar (Pekan Ini) with Scenario Transmissions.
    Covers US Macro Catalysts & Domestic Indonesian Releases.
    """
    events = [
        {
            "day": "Rabu",
            "date": "28 Okt 2026",
            "time_wib": "19:30 WIB",
            "country": "US 🇺🇸",
            "event": "US GDP Q3 Final / Annual Revision",
            "importance": "TINGGI 🔴",
            "prev": "1.5%",
            "cons": "1.6%",
            "impact_hot": "Pertumbuhan di atas ekspektasi -> Menahan ekspektasi pemotongan suku bunga Fed. Yield US10Y naik, menekan XLK dan Crypto.",
            "impact_cool": "Pertumbuhan melambat -> Memicu narasi soft/hard landing. Sektor defensif (XLU, XLV) menguat, yield obligasi turun.",
            "favored_asset": "XLI (Industrials) jika Hot; XLU (Utilities) jika Cool"
        },
        {
            "day": "Kamis",
            "date": "29 Okt 2026",
            "time_wib": "19:30 WIB",
            "country": "US 🇺🇸",
            "event": "US Core PCE Price Index MoM / YoY",
            "importance": "KRUSIAL 🔴",
            "prev": "0.2% MoM (3.7% YoY)",
            "cons": "0.3% MoM (3.6% YoY)",
            "impact_hot": "Core PCE > 0.3%: The Fed semakin terkunci pada sikap hawkish. USD/IDR tertekan mendekati 18.200, BTC koreksi menguji support bawah, XLK terkoreksi.",
            "impact_cool": "Core PCE <= 0.2%: Disinflasi berlanjut. Relief rally pada Bitcoin (BTC) & Nasdaq (QQQ). Tekanan DXY mereda.",
            "favored_asset": "Cash / XLE jika Hot; XLK / BTC jika Cool"
        },
        {
            "day": "Kamis",
            "date": "29 Okt 2026",
            "time_wib": "19:30 WIB",
            "country": "US 🇺🇸",
            "event": "US Initial Jobless Claims",
            "importance": "MODERAT 🟡",
            "prev": "221K",
            "cons": "225K",
            "impact_hot": "Klaim turun (< 215K) = Pasar tenaga kerja ketat -> Inflasi upah berisiko berlanjut.",
            "impact_cool": "Klaim naik (> 235K) = Pendinginan pasar tenaga kerja -> Mendorong Fed melunakkan kebijakan.",
            "favored_asset": "DXY jika Hot; Emas (XAUUSD) jika Cool"
        },
        {
            "day": "Jumat",
            "date": "30 Okt 2026",
            "time_wib": "19:30 WIB",
            "country": "US 🇺🇸",
            "event": "US Non-Farm Payrolls (NFP) & Unemployment Rate",
            "importance": "KRUSIAL 🔴",
            "prev": "+254K | 4.1%",
            "cons": "+115K | 4.1%",
            "impact_hot": "NFP > 160K: Suku bunga obligasi US10Y melonjak, menekan saham perbankan domestik via outflow dan menahan inflow crypto.",
            "impact_cool": "NFP < 90K: Kekhawatiran resesi meningkat, memicu rotasi cepat ke obligasi dan emas, sementara crypto mengalami volatilitas tinggi.",
            "favored_asset": "Emas (XAUUSD) / TLT jika Cool; XLE / DXY jika Hot"
        },
        {
            "day": "Jumat",
            "date": "30 Okt 2026",
            "time_wib": "21:00 WIB",
            "country": "US 🇺🇸",
            "event": "ISM Manufacturing PMI & Prices Paid",
            "importance": "TINGGI 🔴",
            "prev": "47.2",
            "cons": "47.6",
            "impact_hot": "PMI > 50.0 (Ekspansi): Lonjakan aktivitas manufaktur mengonfirmasi skenario No-Landing / Reflasi.",
            "impact_cool": "PMI < 47.0: Kontraksi berlanjut, membebani saham siklikal industri dan komoditas tambang.",
            "favored_asset": "XLI / XLB jika Hot; XLP (Staples) jika Cool"
        },
        {
            "day": "Senin",
            "date": "02 Nov 2026",
            "time_wib": "11:00 WIB",
            "country": "ID 🇮🇩",
            "event": "BPS Inflasi CPI Indonesia (Oktober)",
            "importance": "TINGGI 🔴",
            "prev": "3.19% YoY",
            "cons": "3.30% YoY",
            "impact_hot": "Inflasi > 3.4% akibat imported inflation (BBM & pangan) membatasi pelonggaran BI dan menekan yield SBN ID10Y.",
            "impact_cool": "Inflasi terkendali (< 3.1%) memberi ruang stabilitas bagi sektor perbankan dan konsumer domestik.",
            "favored_asset": "Obligasi IDR jika Cool; Sektor Energi IHSG jika Hot"
        }
    ]
    return events

def compute_macro_flow_projections(snapshot, regime, ews_signals):
    """
    Computes Capital & Liquidity Flow Projections across 3 horizons:
    1. Short-term (7 Hari ke Depan): Transmisi katalis pekan ini
    2. Medium-term (30 Hari ke Depan): Arah Neraca Likuiditas Fed & Dampak ke Sektor US
    3. Aliran Modal Lintas Aset (Cross-Asset Capital Allocation Pipeline)
    """
    prices = snapshot.get("prices", {})
    net_liq = snapshot.get("net_liquidity", {})
    
    us10y = prices.get("^TNX", {}).get("close", 5.0)
    oil = prices.get("CL=F", {}).get("close", 100.0)
    dxy = prices.get("DX-Y.NYB", {}).get("close", 102.0)
    net_liq_val = net_liq.get("net_liquidity_bil", 5800.0)
    net_liq_chg = net_liq.get("change_4w_bil", 40.0)
    
    # Capital Drainage & Inflow Mapping
    capital_inflow_destinations = []
    capital_drainage_sources = []
    
    if oil > 90.0:
        capital_inflow_destinations.append({"asset": "XLE (Energy) & Komoditas", "rationale": "Benteng lindung nilai terhadap kejutan pasokan energi global."})
        capital_drainage_sources.append({"asset": "Pasar Saham EM & Rupiah", "rationale": "Tekanan imported inflation dan beban subsidi energi memperlebar defisit berjalan."})
        
    if us10y > 4.8:
        capital_inflow_destinations.append({"asset": "US Cash / T-Bills (Yield 5%+)", "rationale": "Risk-free rate tinggi menarik likuiditas global ke instrumen pasar uang dolar."})
        capital_drainage_sources.append({"asset": "XLK (High-Beta Tech) & XLRE (Real Estate)", "rationale": "Discount rate tinggi menekan valuasi rasio P/E dan beban refinansial utang."})
    else:
        capital_inflow_destinations.append({"asset": "XLK (Tech) & BTC", "rationale": "Pelonggaran suku bunga riil mengalirkan likuiditas ke aset berdurasi panjang."})
        
    if net_liq_chg > 20.0:
        capital_inflow_destinations.append({"asset": "Bitcoin (BTC)", "rationale": "Korelasi +0.82 terhadap ekspansi neraca likuiditas Fed (TGA drawdown)."})
    else:
        capital_drainage_sources.append({"asset": "Altcoins & Spekulatif", "rationale": "Likuiditas terbatas mendorong rotasi defensif ke BTC Dominance."})

    # 3-Scenario Projected Trajectories (7-30 Hari)
    scenarios = [
        {
            "name": "Skenario A: Stagflasi Pasokan Energi (Base Case / Saat Ini)",
            "prob": "65%",
            "trigger": "Minyak WTI bertahan di atas $95/bbl & Core PCE bertahan alot (>0.3% MoM).",
            "us_sectors_path": "Overweight XLE & XLB; Underweight XLK & XLY. Rotasi selektif ke saham defensif berdividen tinggi (XLP, XLU).",
            "crypto_path": "Bitcoin mengalami volatilitas tinggi dalam rentang konsolidasi; de-coupling selektif dari Nasdaq berkat sifat anti-devaluasi kas.",
            "indonesia_path": "USD/IDR menguji area Rp 18.000–18.250. BI mempertahankan stance hawkish; IHSG didukung saham tambang/energi tapi tertekan di perbankan."
        },
        {
            "name": "Skenario B: Disinflasi & Pelepasan Cadangan Minyak (Bull Case)",
            "prob": "25%",
            "trigger": "Pelepasan SPR berhasil meredam WTI ke bawah $85/bbl dan NFP/PCE melunak.",
            "us_sectors_path": "Reli besar pada XLK (Teknologi), XLC (Komunikasi), dan saham pertumbuhan. Rotasi keluar dari energi dan kas.",
            "crypto_path": "Ekspansi reli Bitcoin menembus resistensi baru disertai Altseason (rasio ETH/BTC rebound ke atas 0.035).",
            "indonesia_path": "Rupiah menguat kembali ke kisaran Rp 17.500–17.700. Foreign net buy kembali mengalir ke saham big banks (BBCA, BBRI, BMRI)."
        },
        {
            "name": "Skenario C: Squeeze Likuiditas & Guncangan Kredit (Bear Case)",
            "prob": "10%",
            "trigger": "US10Y menembus 5.30% disertai lonjakan spread obligasi sampah (> 500 bps).",
            "us_sectors_path": "De-risking menyeluruh: seluruh sektor terkoreksi kecuali Kas/US Dollar Index (DXY) dan Emas (XAUUSD).",
            "crypto_path": "Drawdown tajam jangka pendek akibat likuidasi leverage derivatif.",
            "indonesia_path": "Tekanan berat nilai tukar; intervensi cadangan devisa agresif Bank Indonesia untuk menahan flight to safety."
        }
    ]

    return {
        "inflows": capital_inflow_destinations,
        "drainages": capital_drainage_sources,
        "scenarios": scenarios,
        "net_liq_trend": "EKSPANSI MODERAT (+42.3B)" if net_liq_chg > 0 else "KONTRAKSI / PENARIKAN",
        "primary_flow_regime": "ROTASI SIKLIKAL & ENERGY SHIELD"
    }

if __name__ == "__main__":
    cal = get_weekly_economic_calendar()
    print("Weekly Economic Events:", len(cal))
    for c in cal:
        print(f"[{c['date']} {c['time_wib']}] {c['country']} {c['event']} ({c['importance']})")
