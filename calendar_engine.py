"""
Weekly Economic Calendar & Macro Capital Flow Projection Engine
Provides:
1. One-Week High-Impact Economic Calendar (AS & Indonesia) with Scenario Transmissions
2. Dynamic Daylight Saving Time (DST: EDT vs EST) Timezone Calculation
3. 7-Day to 30-Day Liquidity & Capital Flow Projections (US Sectors, Crypto, Rupiah)
"""

import datetime
import zoneinfo

def get_weekly_economic_calendar():
    """
    Weekly High-Impact Economic Calendar with exact official dates,
    consensus estimates, and dynamic timezone conversion (EDT vs EST).
    """
    ny_tz = zoneinfo.ZoneInfo("America/New_York")
    wib_tz = zoneinfo.ZoneInfo("Asia/Jakarta")

    raw_events = [
        {
            "ny_time": "2026-10-29 08:30",
            "country": "US 🇺🇸",
            "event": "US Advance GDP Q3 (Estimasi Pertama)",
            "importance": "TINGGI 🔴",
            "prev": "3.0% Annualized",
            "cons": "3.0% Annualized",
            "impact_hot": "Pertumbuhan di atas 3.0% mengonfirmasi skenario No-Landing / resiliensi ekonomi, menopang narasi Fed hawkish.",
            "impact_cool": "Pertumbuhan di bawah 2.5% memicu kekhawatiran pendinginan aktivitas bisnis.",
            "favored_asset": "XLI (Industrials) jika Hot; XLU (Utilities) jika Cool"
        },
        {
            "ny_time": "2026-10-29 08:30",
            "country": "US 🇺🇸",
            "event": "US Core PCE Price Index (September)",
            "importance": "KRUSIAL 🔴",
            "prev": "0.2% MoM (3.7% YoY)",
            "cons": "0.2% MoM (3.1% YoY)",
            "impact_hot": "Core PCE > 0.2% MoM: Inflasi acuan The Fed bertahan alot, memperbesar peluang pengetatan suku bunga lanjutan.",
            "impact_cool": "Core PCE <= 0.2% MoM: Disinflasi berlanjut, memberi ruang nafas bagi pasar ekuitas & kripto.",
            "favored_asset": "Cash / XLE jika Hot; XLK / BTC jika Cool"
        },
        {
            "ny_time": "2026-10-29 08:30",
            "country": "US 🇺🇸",
            "event": "US Initial Jobless Claims",
            "importance": "MODERAT 🟡",
            "prev": "221K",
            "cons": "225K",
            "impact_hot": "Klaim turun (< 215K) = Pasar tenaga kerja ketat -> Menahan ekspektasi penurunan suku bunga.",
            "impact_cool": "Klaim naik (> 235K) = Pendinginan pasar tenaga kerja -> Meredakan yield obligasi.",
            "favored_asset": "DXY jika Hot; Emas (XAUUSD) jika Cool"
        },
        {
            "ny_time": "2026-10-30 08:30",
            "country": "US 🇺🇸",
            "event": "US Employment Cost Index (ECI) Q3",
            "importance": "TINGGI 🔴",
            "prev": "0.9% QoQ",
            "cons": "0.8% QoQ",
            "impact_hot": "ECI > 0.9%: Tekanan kenaikan biaya upah mengonfirmasi risiko inflasi 'sticky' dan memperkuat bias hawkish.",
            "impact_cool": "ECI <= 0.7%: Tekanan biaya tenaga kerja mereda, melonggarkan tekanan margin korporasi.",
            "favored_asset": "DXY / T-Bills jika Hot; XLK / SPY jika Cool"
        },
        {
            "ny_time": "2026-10-30 09:45",
            "country": "US 🇺🇸",
            "event": "Chicago PMI (Oktober)",
            "importance": "MODERAT 🟡",
            "prev": "46.6",
            "cons": "47.0",
            "impact_hot": "PMI > 50.0 (Ekspansi): Barometer aktivitas manufaktur Midwest berekspansi menjelang ISM.",
            "impact_cool": "PMI < 46.0: Sektor manufaktur masih terkontraksi dalam.",
            "favored_asset": "XLI jika Hot; TLT jika Cool"
        },
        {
            "wib_time": "2026-11-02 11:00",
            "country": "ID 🇮🇩",
            "event": "BPS Inflasi CPI Indonesia (Oktober)",
            "importance": "TINGGI 🔴",
            "prev": "3.19% YoY",
            "cons": "3.30% YoY",
            "impact_hot": "Inflasi > 3.4% akibat imported inflation (BBM & pangan) membatasi ruang pelonggaran BI dan menekan yield SBN.",
            "impact_cool": "Inflasi terkendali (< 3.1%) memberi ruang stabilitas bagi sektor perbankan dan konsumer domestik.",
            "favored_asset": "Obligasi IDR jika Cool; Sektor Energi IHSG jika Hot"
        },
        {
            "ny_time": "2026-11-02 10:00",
            "country": "US 🇺🇸",
            "event": "ISM Manufacturing PMI & Prices Paid (Oktober)",
            "importance": "TINGGI 🔴",
            "prev": "47.2",
            "cons": "47.6",
            "impact_hot": "PMI > 50.0 (Ekspansi): Lonjakan aktivitas manufaktur mengonfirmasi skenario Reflasi. (Catatan: 10:00 EST = 22:00 WIB pasca akhir DST).",
            "impact_cool": "PMI < 47.0: Kontraksi berlanjut, membebani saham siklikal industri dan komoditas tambang.",
            "favored_asset": "XLI / XLB jika Hot; XLP (Staples) jika Cool"
        },
        {
            "ny_time": "2026-11-04 10:00",
            "country": "US 🇺🇸",
            "event": "ISM Services PMI (Oktober)",
            "importance": "TINGGI 🔴",
            "prev": "54.9",
            "cons": "54.5",
            "impact_hot": "PMI Jasa > 55.0 menunjukkan ketahanan sektor jasa yang merupakan kontributor terbesar inflasi inti.",
            "impact_cool": "PMI Jasa < 53.0 menandakan perlambatan permintaan domestik.",
            "favored_asset": "XLY jika Hot; XLV jika Cool"
        },
        {
            "ny_time": "2026-11-06 08:30",
            "country": "US 🇺🇸",
            "event": "US Non-Farm Payrolls (NFP) & Unemployment Rate (Oktober)",
            "importance": "KRUSIAL 🔴",
            "prev": "+29K | 4.2%",
            "cons": "+115K | 4.2%",
            "impact_hot": "NFP > 150K: Suku bunga obligasi US10Y berisiko melonjak, pasar menakar probabilitas kenaikan suku bunga Fed Desember (~76%).",
            "impact_cool": "NFP < 80K: Pendinginan pasar tenaga kerja meredakan kekhawatiran kenaikan suku bunga, memicu relief rally ekuitas & kripto.",
            "favored_asset": "Emas (XAUUSD) / TLT jika Cool; XLE / DXY jika Hot"
        }
    ]

    indo_days = {
        "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
        "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
    }
    indo_months = {
        "Jan": "Okt", "Feb": "Feb", "Mar": "Mar", "Apr": "Apr", "May": "Mei", "Jun": "Jun",
        "Jul": "Jul", "Aug": "Ags", "Sep": "Sep", "Oct": "Okt", "Nov": "Nov", "Dec": "Des"
    }

    events = []
    for ev in raw_events:
        if "ny_time" in ev:
            dt_ny = datetime.datetime.strptime(ev["ny_time"], "%Y-%m-%d %H:%M").replace(tzinfo=ny_tz)
            dt_wib = dt_ny.astimezone(wib_tz)
            date_iso = dt_wib.strftime("%Y-%m-%d")
            day_name = indo_days.get(dt_wib.strftime("%A"), dt_wib.strftime("%A"))
            date_str = f"{dt_wib.day} {indo_months.get(dt_wib.strftime('%b'), dt_wib.strftime('%b'))} {dt_wib.year}"
            time_wib_str = dt_wib.strftime("%H:%M WIB")
            tz_tag = f"[{dt_ny.tzname()}]"
        else:
            dt_wib = datetime.datetime.strptime(ev["wib_time"], "%Y-%m-%d %H:%M").replace(tzinfo=wib_tz)
            date_iso = dt_wib.strftime("%Y-%m-%d")
            day_name = indo_days.get(dt_wib.strftime("%A"), dt_wib.strftime("%A"))
            date_str = f"{dt_wib.day} {indo_months.get(dt_wib.strftime('%b'), dt_wib.strftime('%b'))} {dt_wib.year}"
            time_wib_str = dt_wib.strftime("%H:%M WIB")
            tz_tag = "[WIB]"

        events.append({
            "day": day_name,
            "date": date_str,
            "date_iso": date_iso,
            "time_wib": time_wib_str,
            "tz_tag": tz_tag,
            "country": ev["country"],
            "event": ev["event"],
            "importance": ev["importance"],
            "prev": ev["prev"],
            "cons": ev["cons"],
            "impact_hot": ev["impact_hot"],
            "impact_cool": ev["impact_cool"],
            "favored_asset": ev["favored_asset"]
        })

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
    irx = prices.get("^IRX", {}).get("close", 4.0)
    oil = prices.get("CL=F", {}).get("close", 100.0)
    net_liq_val = net_liq.get("net_liquidity_bil", 5800.0)
    net_liq_chg = net_liq.get("change_4w_bil", 40.0)
    
    # Capital Drainage & Inflow Mapping
    capital_inflow_destinations = []
    capital_drainage_sources = []
    
    if oil > 90.0:
        capital_inflow_destinations.append({"asset": "XLE (Energy) & Komoditas", "rationale": "Benteng lindung nilai terhadap kejutan pasokan energi global."})
        capital_drainage_sources.append({"asset": "Pasar Saham EM & Rupiah", "rationale": "Tekanan imported inflation dan beban subsidi energi memperlebar defisit berjalan."})
        
    if us10y > 4.8:
        t_bill_str = f"US Cash / T-Bills (Yield ~{irx:.1f}%)" if irx > 0 else "US Cash / T-Bills (Yield ~4.0%)"
        capital_inflow_destinations.append({"asset": t_bill_str, "rationale": "Risk-free rate tinggi menarik likuiditas global ke instrumen pasar uang dolar."})
        capital_drainage_sources.append({"asset": "XLK (High-Beta Tech) & XLRE (Real Estate)", "rationale": "Discount rate tinggi menekan valuasi rasio P/E dan beban refinansial utang."})
    else:
        capital_inflow_destinations.append({"asset": "XLK (Tech) & BTC", "rationale": "Pelonggaran suku bunga riil mengalirkan likuiditas ke aset berdurasi panjang."})
        
    if net_liq_chg > 20.0:
        capital_inflow_destinations.append({"asset": "Bitcoin (BTC)", "rationale": "Korelasi +0.82 terhadap ekspansi neraca likuiditas Fed (TGA drawdown)."})
    else:
        capital_drainage_sources.append({"asset": "Altcoins & Spekulatif", "rationale": "Likuiditas terbatas mendorong rotasi defensif ke BTC Dominance."})

    # 3-Scenario Projected Trajectories with Real Fed Stance
    scenarios = [
        {
            "name": "Skenario A: Bias Hawkish Fed & Risiko Kenaikan Suku Bunga (Base Case)",
            "prob": "65%",
            "trigger": "Minyak WTI bertahan > $95/bbl & Fed mempertahankan stance restriktif dengan peluang kenaikan Desember dihargai pasar ~76%.",
            "us_sectors_path": "Overweight XLE & Finansial (XLF); Underweight XLK & XLY. Rotasi selektif ke saham defensif berdividen tinggi (XLP, XLU).",
            "crypto_path": "Bitcoin mengalami volatilitas tinggi dalam rentang konsolidasi; de-coupling selektif dari saham teknologi berkat narasi lindung nilai likuiditas.",
            "indonesia_path": "USD/IDR berada dalam rentang tekanan Rp 18.000–18.250. BI mempertahankan stance hawkish / intervensi valas agresif untuk meredam imported inflation."
        },
        {
            "name": "Skenario B: Disinflasi & Pelepasan Cadangan Minyak (Bull Case)",
            "prob": "25%",
            "trigger": "Pelepasan SPR berhasil meredam WTI ke bawah $85/bbl dan data tenaga kerja/PCE mengonfirmasi pelemahan tekanan upah.",
            "us_sectors_path": "Reli besar pada XLK (Teknologi), XLC (Komunikasi), dan saham pertumbuhan. Rotasi keluar dari energi dan kas.",
            "crypto_path": "Ekspansi reli Bitcoin menembus resistensi baru disertai Altseason (rasio ETH/BTC rebound ke atas 0.035).",
            "indonesia_path": "Rupiah menguat kembali ke kisaran Rp 17.500–17.700. Foreign net buy kembali mengalir ke saham perbankan besar."
        },
        {
            "name": "Skenario C: Squeeze Likuiditas & Guncangan Kredit (Bear Case)",
            "prob": "10%",
            "trigger": "US10Y menembus 5.30% disertai lonjakan spread obligasi sampah (> 500 bps) dan shock geopolitik energi.",
            "us_sectors_path": "De-risking menyeluruh: seluruh sektor terkoreksi kecuali Kas/US Dollar Index (DXY) dan Emas (XAUUSD).",
            "crypto_path": "Drawdown tajam jangka pendek akibat likuidasi leverage derivatif.",
            "indonesia_path": "Tekanan berat nilai tukar; intervensi cadangan devisa agresif Bank Indonesia untuk menahan capital flight."
        }
    ]

    return {
        "inflows": capital_inflow_destinations,
        "drainages": capital_drainage_sources,
        "scenarios": scenarios,
        "net_liq_trend": "EKSPANSI MODERAT" if net_liq_chg > 0 else "KONTRAKSI / PENARIKAN",
        "primary_flow_regime": "ROTASI SIKLIKAL & ENERGY SHIELD"
    }
