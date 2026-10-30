"""
Analytics & Quantitative Macro Engine for US Sectors and Crypto
Computes:
1. Early Warning Signals (EWS) with institutional thresholds
2. 4-Quadrant Macro Regime Classification
3. Cross-Asset Rolling Correlation Matrix (with BREAK / INVERT detection)
4. S&P 500 11 Sector & Crypto Tactical Scorecard
"""

import sqlite3
import pandas as pd
import numpy as np
from config import DB_PATH, EWS_THRESHOLDS, TICKERS_SECTORS, TICKERS_CRYPTO

def load_price_history():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT date, ticker, close FROM market_prices ORDER BY date ASC", conn)
    conn.close()
    if df.empty:
        return pd.DataFrame()
    pivot = df.pivot(index="date", columns="ticker", values="close")
    return pivot

def evaluate_ews(snapshot):
    prices = snapshot.get("prices", {})
    fred = snapshot.get("fred", {})
    net_liq = snapshot.get("net_liquidity", {})
    
    signals = []
    
    # 1. US 10Y Yield Level
    tnx = prices.get("^TNX", {}).get("close", 0)
    if tnx > EWS_THRESHOLDS["US10Y_CRITICAL"]:
        status = "BAHAYA"
        ctx = f"Yield 10Y di level restriktif {tnx:.3f}%, menaikkan discount rate aset durasi panjang (Tech & Crypto)."
    elif tnx > 4.2:
        status = "WASPADA"
        ctx = f"Yield 10Y {tnx:.3f}%, zona moderat-tinggi."
    else:
        status = "AMAN"
        ctx = f"Yield 10Y {tnx:.3f}%, terkendali."
    signals.append({
        "name": "US 10Y Treasury Yield",
        "value": f"{tnx:.3f}%",
        "status": status,
        "context": ctx
    })
    
    # 2. Yield Curve Slope (10Y - 3M)
    irx = prices.get("^IRX", {}).get("close", 0)
    spread_10y_3m = (tnx - irx) * 100.0  # in bps
    if spread_10y_3m < 0:
        status = "WASPADA"
        ctx = f"Kurva inverted ({spread_10y_3m:.1f} bps) - sinyal historis pengetatan likuiditas dan resesi lanjutan."
    elif spread_10y_3m > 50:
        status = "AMAN" if tnx < 4.5 else "WASPADA"
        ctx = f"Kurva un-inverting / steepening ({spread_10y_3m:.1f} bps)."
    else:
        status = "AMAN"
        ctx = f"Spread {spread_10y_3m:.1f} bps mendekati netral."
    signals.append({
        "name": "Yield Curve (10Y - 3M T-Bill)",
        "value": f"{spread_10y_3m:+.1f} bps",
        "status": status,
        "context": ctx
    })
    
    # 3. Real Interest Rate (10Y TIPS - DFII10)
    real_rate = fred.get("DFII10", {}).get("value", 0)
    if real_rate >= EWS_THRESHOLDS["REAL_YIELD_TIGHT"]:
        status = "BAHAYA"
        ctx = f"Suku bunga riil {real_rate:.2f}% di atas 2.0% membatasi ekspansi PE ratio Tech dan apresiasi Crypto."
    elif real_rate >= 1.5:
        status = "WASPADA"
        ctx = f"Suku bunga riil {real_rate:.2f}% berada di zona ketat."
    else:
        status = "AMAN"
        ctx = f"Suku bunga riil {real_rate:.2f}% akomodatif."
    signals.append({
        "name": "US 10Y Real Yield (TIPS)",
        "value": f"{real_rate:.2f}%",
        "status": status,
        "context": ctx
    })
    
    # 4. High Yield Credit Spread (BAMLH0A0HYM2)
    hy_spread = fred.get("BAMLH0A0HYM2", {}).get("value", 0) * 100.0  # to bps
    if hy_spread > EWS_THRESHOLDS["HY_SPREAD_STRESS"]:
        status = "BAHAYA"
        ctx = f"Spread obligasi sampah {hy_spread:.0f} bps mengindikasikan tekanan likuiditas kredit korporasi."
    elif hy_spread > EWS_THRESHOLDS["HY_SPREAD_WIDENING"]:
        status = "WASPADA"
        ctx = f"Spread {hy_spread:.0f} bps mulai melebar di atas rata-rata historis."
    else:
        status = "AMAN"
        ctx = f"Spread {hy_spread:.0f} bps rendah - pasar kredit korporasi tenang."
    signals.append({
        "name": "US High Yield Credit Spread",
        "value": f"{hy_spread:.0f} bps",
        "status": status,
        "context": ctx
    })
    
    # 5. CBOE VIX (Equity Volatility)
    vix = prices.get("^VIX", {}).get("close", 0)
    if vix >= EWS_THRESHOLDS["VIX_PANIC"]:
        status = "BAHAYA"
        ctx = f"VIX {vix:.2f} di zona kepanikan ekuitas (>30)."
    elif vix >= EWS_THRESHOLDS["VIX_ELEVATED"]:
        status = "WASPADA"
        ctx = f"VIX {vix:.2f} meningkat (20-30)."
    else:
        status = "AMAN"
        ctx = f"VIX {vix:.2f} relatif stabil di bawah 20."
    signals.append({
        "name": "CBOE Volatility Index (VIX)",
        "value": f"{vix:.2f}",
        "status": status,
        "context": ctx
    })
    
    # 6. Fed Net Liquidity 4-Week Delta
    net_liq_val = net_liq.get("net_liquidity_bil", 0)
    net_liq_chg = net_liq.get("change_4w_bil", 0)
    if net_liq_chg <= -50.0:
        status = "BAHAYA"
        ctx = f"Pengetatan likuiditas bersih Fed −${abs(net_liq_chg):.1f}B dalam 4 minggu terakhir."
    elif net_liq_chg < 0:
        status = "WASPADA"
        ctx = f"Likuiditas bersih melandai tipis (${net_liq_chg:+.1f}B 4W)."
    else:
        status = "AMAN"
        ctx = f"Injeksi likuiditas bersih Fed +${net_liq_chg:.1f}B (Katalis positif BTC & Growth)."
    signals.append({
        "name": "Fed Net Liquidity (4W Delta)",
        "value": f"${net_liq_val:,.1f}B ({net_liq_chg:+.1f}B)",
        "status": status,
        "context": ctx
    })
    
    # 7. US Dollar Index (DXY)
    dxy = prices.get("DX-Y.NYB", {}).get("close", 0)
    if dxy > 105.0:
        status = "BAHAYA"
        ctx = f"Dolar {dxy:.2f} sangat kuat, menekan likuiditas global dan aset berisiko."
    elif dxy > 102.5:
        status = "WASPADA"
        ctx = f"DXY {dxy:.2f} berada di area resistensi."
    else:
        status = "AMAN"
        ctx = f"DXY {dxy:.2f} lemah/stabil, suportif untuk komoditas & crypto."
    signals.append({
        "name": "US Dollar Index (DXY)",
        "value": f"{dxy:.2f}",
        "status": status,
        "context": ctx
    })
    
    # 8. WTI Crude Oil
    oil = prices.get("CL=F", {}).get("close", 0)
    if oil >= 90.0:
        status = "BAHAYA"
        ctx = f"Minyak ${oil:.2f}/bbl memicu risiko stagflasi dan kenaikan ekspektasi inflasi."
    elif oil >= 80.0:
        status = "WASPADA"
        ctx = f"Minyak ${oil:.2f}/bbl di level waspada."
    else:
        status = "AMAN"
        ctx = f"Minyak ${oil:.2f}/bbl moderat, meredam inflasi energi."
    signals.append({
        "name": "WTI Crude Oil",
        "value": f"${oil:.2f}",
        "status": status,
        "context": ctx
    })

    # 9. USD / IDR (Kurs Rupiah)
    usdidr = prices.get("USDIDR=X", {}).get("close", 0)
    if usdidr > 18000:
        status = "BAHAYA"
        ctx = f"Rupiah tertekan di Rp {usdidr:,.0f} melampaui level Rp 18.000, memicu intervensi cadangan devisa agresif BI."
    elif usdidr > 16500:
        status = "WASPADA"
        ctx = f"Rupiah Rp {usdidr:,.0f} di atas batas nyaman BI, menahan ruang penurunan suku bunga BI-Rate."
    else:
        status = "AMAN"
        ctx = f"Rupiah stabil di kisaran Rp {usdidr:,.0f}."
    signals.append({
        "name": "USD / IDR (Kurs Rupiah)",
        "value": f"Rp {usdidr:,.0f}",
        "status": status,
        "context": ctx
    })

    # 10. Emas / XAUUSD
    gold = prices.get("GC=F", {}).get("close", 0)
    if gold > 3800:
        status = "WASPADA" if tnx > 4.5 else "AMAN"
        ctx = f"Emas XAUUSD di level rekor ${gold:,.1f}/oz mencerminkan lindung nilai geopolitik & de-dolarisasi global."
    else:
        status = "AMAN"
        ctx = f"Emas XAUUSD di level ${gold:,.1f}/oz stabil."
    signals.append({
        "name": "Emas (XAUUSD)",
        "value": f"${gold:,.1f}/oz",
        "status": status,
        "context": ctx
    })
    
    return signals

def classify_macro_regime(snapshot, ews_signals):
    """
    Classify into 4 Quadrants:
    1. DISINFLATIONARY_BOOM (Goldilocks: Growth Up, Inflation Down)
    2. REFLATION (Growth Up, Inflation Up)
    3. STAGFLATION (Growth Down, Inflation Up)
    4. DEFLATIONARY_CONTRACTION (Growth Down, Inflation Down)
    """
    prices = snapshot.get("prices", {})
    oil = prices.get("CL=F", {}).get("close", 75)
    vix = prices.get("^VIX", {}).get("close", 18)
    net_liq_chg = snapshot.get("net_liquidity", {}).get("change_4w_bil", 0)
    tnx = prices.get("^TNX", {}).get("close", 4.0)
    
    # Danger count in EWS
    bahaya_count = sum(1 for s in ews_signals if s["status"] == "BAHAYA")
    waspada_count = sum(1 for s in ews_signals if s["status"] == "WASPADA")
    
    if oil > 88.0 and tnx > 4.5:
        regime = "STAGFLASI"
        title = "STAGFLASI ENERGI & SQUEEZE BIAYA"
        summary = "Tekanan pasokan komoditas energi menaikkan yield dan membatasi ruang pelonggaran bank sentral, menekan margin emiten non-energi."
        analog = "1973 Oil Shock / Q2 2022 Fed Rate Shock"
        favored_sectors = ["XLE (Energy)", "XLB (Materials)", "Cash / Bil"]
        lagging_sectors = ["XLK (Tech)", "XLY (Discretionary)", "XLRE (Real Estate)"]
        crypto_stance = "DEFENSIVE / VOLATILE (Tunggu stabilisasi yield real)"
    elif net_liq_chg > 20 and vix < 20 and tnx < 4.4:
        regime = "DISINFLASI_BOOM"
        title = "DISINFLASI & EKSPANSI LIKUIDITAS"
        summary = "Likuiditas bank sentral ekspansif berdampingan dengan volatilitas rendah dan inflasi terkendali. Lingkungan paling ideal untuk High-Beta."
        analog = "2020-2021 QE Expansion / 1995-1998 Tech Boom"
        favored_sectors = ["XLK (Tech)", "XLC (Communication)", "XLY (Discretionary)"]
        lagging_sectors = ["XLU (Utilities)", "XLP (Staples)"]
        crypto_stance = "AGGRESSIVE RISK-ON (BTC + High Beta Altcoins)"
    elif oil > 80.0 and vix < 22 and tnx > 4.2:
        regime = "REFLASI"
        title = "REFLASI & ROTASI SIKLIKAL"
        summary = "Pertumbuhan ekonomi solid diiringi kenaikan harga komoditas dan yield. Sektor siklikal dan finansial memimpin rotasi."
        analog = "2004-2006 Commodity Supercycle / 2017 Global Reflation"
        favored_sectors = ["XLF (Financials)", "XLI (Industrials)", "XLE (Energy)"]
        lagging_sectors = ["XLU (Utilities)", "XLRE (Real Estate)"]
        crypto_stance = "SELECTIVE RISK-ON (BTC dominan, selektif Altcoins)"
    else:
        regime = "DEFLASI_KONTRAKSI"
        title = "DEFENSIVE LATE-CYCLE / KONTRAKSI"
        summary = "Permintaan agregat melambat, volatilitas meningkat, dan premi risiko kredit melebar. Rotasi ketat ke sektor defensif."
        analog = "2008 GFC Pre-crisis / 2001 Tech Hangover"
        favored_sectors = ["XLU (Utilities)", "XLV (Healthcare)", "XLP (Staples)"]
        lagging_sectors = ["XLK (Tech)", "XLY (Discretionary)", "XLI (Industrials)"]
        crypto_stance = "RISK-OFF / CAPITAL PRESERVATION (Cash & Stables)"
        
    return {
        "regime_id": regime,
        "title": title,
        "summary": summary,
        "analog": analog,
        "favored_sectors": favored_sectors,
        "lagging_sectors": lagging_sectors,
        "crypto_stance": crypto_stance,
        "score_bahaya": bahaya_count,
        "score_waspada": waspada_count
    }

def compute_correlation_matrix(price_df, window=30):
    if price_df.empty or len(price_df) < 15:
        return []
    
    # Calculate daily returns
    returns = price_df.ffill().pct_change().dropna()
    corr = returns.tail(window).corr()
    
    pairs = [
        {"pair": "BTC-USD ↔ QQQ", "a": "BTC-USD", "b": "QQQ", "normal": "+0.60 to +0.85", "desc": "Korelasi High-Beta Tech vs Crypto"},
        {"pair": "BTC-USD ↔ DX-Y.NYB", "a": "BTC-USD", "b": "DX-Y.NYB", "normal": "-0.50 to -0.75", "desc": "Korelasi Likuiditas Dolar vs Bitcoin"},
        {"pair": "XLK ↔ ^TNX", "a": "XLK", "b": "^TNX", "normal": "-0.40 to -0.65", "desc": "Tekanan Discount Rate pada Sektor Teknologi"},
        {"pair": "XLE ↔ CL=F", "a": "XLE", "b": "CL=F", "normal": "+0.70 to +0.90", "desc": "Transmisi Harga Minyak ke Sektor Energi"},
        {"pair": "^VIX ↔ SPY", "a": "^VIX", "b": "SPY", "normal": "-0.70 to -0.85", "desc": "Inversi Volatilitas terhadap Indeks Saham"},
        {"pair": "GC=F ↔ DX-Y.NYB", "a": "GC=F", "b": "DX-Y.NYB", "normal": "-0.40 to -0.60", "desc": "Inversi Dolar terhadap Emas"},
    ]
    
    results = []
    for p in pairs:
        a = p["a"]
        b = p["b"]
        if a in corr.columns and b in corr.columns:
            r = corr.loc[a, b]
            if np.isnan(r):
                continue
            
            # Detect Break or Invert
            status = "NORMAL"
            if "to -" in p["normal"] and r > 0.15:
                status = "INVERT"
            elif "to +" in p["normal"] and r < -0.15:
                status = "INVERT"
            elif abs(r) < 0.20:
                status = "BREAK"
                
            results.append({
                "pair_name": p["pair"],
                "current_r": round(float(r), 2),
                "expected_range": p["normal"],
                "status": status,
                "notes": p["desc"]
            })
    return results

def compute_sector_scorecard(snapshot, regime_data):
    prices = snapshot.get("prices", {})
    scores = []
    
    for ticker, meta in TICKERS_SECTORS.items():
        data = prices.get(ticker, {})
        c = data.get("close", 0)
        chg_1d = data.get("change_1d_pct", 0)
        chg_5d = data.get("change_5d_pct", 0)
        chg_20d = data.get("change_20d_pct", 0)
        
        # Momentum score
        momentum_score = (chg_1d * 0.2) + (chg_5d * 0.3) + (chg_20d * 0.5)
        
        # Allocation recommendation
        if ticker in [s.split()[0] for s in regime_data["favored_sectors"]]:
            alloc = "OVERWEIGHT (OW)"
            stance = "bullish"
        elif ticker in [s.split()[0] for s in regime_data["lagging_sectors"]]:
            alloc = "UNDERWEIGHT (UW)"
            stance = "bearish"
        else:
            alloc = "NEUTRAL (N)"
            stance = "neutral"
            
        scores.append({
            "ticker": ticker,
            "name": meta["name"],
            "profile": meta["profile"],
            "close": c,
            "chg_1d": chg_1d,
            "chg_5d": chg_5d,
            "chg_20d": chg_20d,
            "momentum_score": round(momentum_score, 2),
            "recommendation": alloc,
            "stance": stance
        })
        
    scores.sort(key=lambda x: x["momentum_score"], reverse=True)
    return scores

def compute_crypto_scorecard(snapshot):
    prices = snapshot.get("prices", {})
    crypto_data = []
    
    btc = prices.get("BTC-USD", {})
    eth = prices.get("ETH-USD", {})
    
    eth_btc_ratio = 0
    if btc.get("close", 0) > 0 and eth.get("close", 0) > 0:
        eth_btc_ratio = round(eth["close"] / btc["close"], 4)
        
    for ticker, meta in TICKERS_CRYPTO.items():
        data = prices.get(ticker, {})
        crypto_data.append({
            "ticker": ticker,
            "name": meta["name"],
            "category": meta["category"],
            "close": data.get("close", 0),
            "chg_1d": data.get("change_1d_pct", 0),
            "chg_5d": data.get("change_5d_pct", 0),
            "chg_20d": data.get("change_20d_pct", 0),
        })
    return crypto_data, eth_btc_ratio

def analyze_indonesia_macro_sentiment(snapshot, ews_signals, regime):
    prices = snapshot.get("prices", {})
    usdidr = prices.get("USDIDR=X", {}).get("close", 18100)
    usdidr_chg = prices.get("USDIDR=X", {}).get("change_1d_pct", 0)
    eido = prices.get("EIDO", {}).get("close", 10.45)
    eido_chg = prices.get("EIDO", {}).get("change_1d_pct", 0)
    us10y = prices.get("^TNX", {}).get("close", 5.0)
    dxy = prices.get("DX-Y.NYB", {}).get("close", 102.0)
    oil = prices.get("CL=F", {}).get("close", 100.0)
    
    # 1. Kurs Rupiah Pressure
    if usdidr > 18000:
        kurs_status = "TEKANAN BERAT"
        kurs_desc = f"USD/IDR di level Rp {usdidr:,.0f} ({usdidr_chg:+.2f}%) menembus ambang batas psikologis 18.000 akibat yield spread US10Y ({us10y:.2f}%) yang tinggi."
    elif usdidr > 16500:
        kurs_status = "WASPADA"
        kurs_desc = f"USD/IDR di Rp {usdidr:,.0f} ({usdidr_chg:+.2f}%) berada di bawah tekanan dolar kuat DXY {dxy:.2f}."
    else:
        kurs_status = "STABIL"
        kurs_desc = f"USD/IDR Rp {usdidr:,.0f} terkendali."
        
    # 2. Bank Indonesia Policy Room
    if us10y > 4.6 or usdidr > 17500:
        bi_status = "HAWKISH / INTERVENSI AGRESIF"
        bi_desc = "Ruang pelonggaran BI-Rate terkunci. BI diwajibkan melakukan intervensi 'Triple Intervention' (DNDF, spot, SBN) dan mengerek instrumen SRBI/SVBI untuk menahan capital flight."
    else:
        bi_status = "NETRAL / AKOMODATIF"
        bi_desc = "Ruang pemangkasan suku bunga terbuka jika inflasi domestik terjaga."
        
    # 3. Beban Fiskal APBN & Energi
    if oil > 90.0:
        apbn_status = "BEBAN SUBSIDI MENINGKAT"
        apbn_desc = f"Harga minyak WTI (${oil:.2f}/bbl) jauh melampaui asumsi ICP APBN, memperlebar defisit subsidi energi dan menekan neraca perdagangan migas."
    else:
        apbn_status = "TERKENDALI"
        apbn_desc = f"Harga minyak ${oil:.2f}/bbl masih dalam batas toleransi fiskal."
        
    # 4. Transmisi ke IHSG & Arus Asing (EIDO)
    if us10y > 4.8 and dxy > 102.0:
        ihsg_status = "RISK-OFF ASING / UNDERPERFORM"
        ihsg_desc = f"EIDO ({eido_chg:+.2f}%) mencerminkan de-risking investor asing dari saham perbankan big-cap (BBCA, BBRI, BMRI). Hanya emiten komoditas energi yang mampu bertahan."
    else:
        ihsg_status = "NETRAL / INFLOW SELEKTIF"
        ihsg_desc = "Arus modal asing selektif masuk ke saham domestik."
        
    summary_paragraph = (
        f"Kombinasi US10Y di level {us10y:.3f}%, DXY {dxy:.2f}, dan WTI Crude ${oil:.2f} memicu transmisi negatif ke Indonesia lewat "
        f"dua saluran utama: depresiasi nilai tukar (USD/IDR Rp {usdidr:,.0f}) dan ancaman 'imported inflation' dari energi. "
        f"Bank Indonesia dipaksa menahan BI-Rate tetap tinggi dan menjaga likuiditas valas, yang berdampak menekan valuasi perbankan "
        f"dan saham blue-chip IHSG, meskipun emiten tambang & batubara mendapat kompensasi dari tingginya harga komoditas."
    )
    
    return {
        "usdidr_val": usdidr,
        "usdidr_chg": usdidr_chg,
        "eido_val": eido,
        "eido_chg": eido_chg,
        "kurs_status": kurs_status,
        "kurs_desc": kurs_desc,
        "bi_status": bi_status,
        "bi_desc": bi_desc,
        "apbn_status": apbn_status,
        "apbn_desc": apbn_desc,
        "ihsg_status": ihsg_status,
        "ihsg_desc": ihsg_desc,
        "summary": summary_paragraph
    }

def analyze_market_drivers(snapshot, regime, ews_signals):
    """
    Automated Causality Engine:
    Answers 'Why is Bitcoin down?', 'Why is Oil up?', 'Fed Liquidity Impact', and 'Macro Regime Triggers'.
    """
    prices = snapshot.get("prices", {})
    net_liq = snapshot.get("net_liquidity", {})
    
    oil = prices.get("CL=F", {}).get("close", 0)
    oil_1d = prices.get("CL=F", {}).get("change_1d_pct", 0)
    oil_20d = prices.get("CL=F", {}).get("change_20d_pct", 0)
    
    btc = prices.get("BTC-USD", {}).get("close", 0)
    btc_1d = prices.get("BTC-USD", {}).get("change_1d_pct", 0)
    btc_20d = prices.get("BTC-USD", {}).get("change_20d_pct", 0)
    
    tnx = prices.get("^TNX", {}).get("close", 0)
    dxy = prices.get("DX-Y.NYB", {}).get("close", 0)
    gold = prices.get("GC=F", {}).get("close", 0)
    
    # 1. Kenapa Minyak Bergerak
    if oil > 90:
        oil_driver = (
            f"Minyak mentah WTI berada di level tinggi (${oil:.2f}/bbl, 20D: {oil_20d:+.1f}%) "
            f"dipicu oleh eskalasi tensi geopolitik Timur Tengah, risiko gangguan pasokan, dan disiplin kuota OPEC+. "
            f"Kenaikan ini mentransmisikan tekanan inflasi energi ke seluruh rantai pasok global dan membatasi ruang pemotongan suku bunga The Fed."
        )
        oil_tag = "Geopolitik & Disrupsi Pasokan"
    elif oil_1d > 1.5:
        oil_driver = (
            f"Minyak mentah WTI melonjak {oil_1d:+.1f}% hari ini ke level ${oil:.2f}/bbl akibat kekhawatiran pasokan jangka pendek "
            f"dan penurunan persediaan cadangan minyak strategis AS."
        )
        oil_tag = "Kekhawatiran Pasokan"
    else:
        oil_driver = (
            f"Minyak mentah WTI diperdagangkan di ${oil:.2f}/bbl (1D: {oil_1d:+.1f}%), berada dalam fase konsolidasi "
            f"antara tarik-menarik perlambatan aktivitas manufaktur global vs ketatnya pasokan fisik komoditas energi."
        )
        oil_tag = "Konsolidasi Pasokan"

    # 2. Kenapa Bitcoin Bergerak
    if btc_1d < -1.0 or btc_20d < -3.0:
        btc_driver = (
            f"Koreksi Bitcoin ke kisaran ${btc:,.0f} (1D: {btc_1d:+.1f}%, 20D: {btc_20d:+.1f}%) dipicu oleh fenomena "
            f"'Yield Shock' (US 10Y Yield di {tnx:.3f}%) dan penguatan Dollar AS (DXY {dxy:.2f}). "
            f"Tingginya yield obligasi bebas risiko menyedot likuiditas pasar, memicu de-risking aset non-yielding, "
            f"serta mempercepat likuidasi posisi 'long' ber-leverage tinggi di pasar derivatif kripto."
        )
        btc_tag = "Yield Shock & Likuidasi Derivatif"
    elif btc_1d > 2.0:
        btc_driver = (
            f"Penguatan Bitcoin ke ${btc:,.0f} (1D: {btc_1d:+.1f}%) didorong oleh arus masuk bersih (net inflows) ETF Spot "
            f"dan pelemahan sesaat yield obligasi yang memicu ekspansi selera risiko (risk-on sentiment)."
        )
        btc_tag = "ETF Inflows & Risk-On"
    else:
        btc_driver = (
            f"Bitcoin diperdagangkan di kisaran ${btc:,.0f} (1D: {btc_1d:+.1f}%), berkonsolidasi di dekat support kritis. "
            f"Pasar kripto sedang menunggu katalis rilis data inflasi (PCE/CPI) dan arah pelonggaran likuiditas bank sentral."
        )
        btc_tag = "Konsolidasi & Menunggu Katalis"

    # 3. Likuiditas The Fed
    liq_bil = net_liq.get("net_liquidity_bil", 0)
    chg_4w = net_liq.get("change_4w_bil", 0)
    fed_driver = (
        f"Likuiditas Bersih The Fed tercatat ${liq_bil:,.1f} Miliar (Perubahan 4 Pekan: {chg_4w:+.1f} Miliar). "
        f"Siklus rilis resmi neraca The Fed (H.4.1) terbit setiap Kamis sore waktu Washington DC (Jumat ~03:30 WIB). "
        f"Perubahan neto diatur oleh saldo TGA Departemen Keuangan AS dan fasilitas Reverse Repo (RRP)."
    )

    # 4. Dinamika Makro Rezim
    regime_driver = (
        f"Status Rezim: '{regime['title']}'. Model 4-kuadran mengunci status ini karena kombinasi Minyak (${oil:.2f} > $88) "
        f"dan Yield 10Y ({tnx:.3f}% > 4.50%). Untuk beralih ke 'Disinflasi / Goldilocks', harga minyak harus turun ke bawah $80 "
        f"dan yield US10Y melandai ke bawah 4.40%."
    )

    return {
        "oil": {"price": oil, "chg_1d": oil_1d, "driver": oil_driver, "tag": oil_tag},
        "crypto": {"price": btc, "chg_1d": btc_1d, "driver": btc_driver, "tag": btc_tag},
        "fed": {"net_liq": liq_bil, "chg_4w": chg_4w, "driver": fed_driver},
        "regime": {"title": regime["title"], "driver": regime_driver}
    }

if __name__ == "__main__":
    from data_fetcher import get_latest_snapshot
    snapshot = get_latest_snapshot()
    price_df = load_price_history()
    
    ews = evaluate_ews(snapshot)
    print("EWS Signals evaluated:", len(ews))
    
    regime = classify_macro_regime(snapshot, ews)
    print("Macro Regime:", regime["title"])
    
    corrs = compute_correlation_matrix(price_df)
    print("Correlation matrix pairs:", len(corrs))
    for c in corrs:
        name_safe = c['pair_name'].replace('↔', '<->')
        print(f"{name_safe}: r = {c['current_r']} ({c['status']})")
        
    sectors = compute_sector_scorecard(snapshot, regime)
    print("Top Sector:", sectors[0]["ticker"], sectors[0]["name"], f"({sectors[0]['momentum_score']})")
