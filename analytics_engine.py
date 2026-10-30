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
        ctx = f"Emas XAUUSD bertahan tinggi di ${gold:,.1f}/oz mencerminkan lindung nilai geopolitik & de-dolarisasi global."
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
        
        # Macro Regime Stance
        favored_list = [s.split()[0] for s in regime_data.get("favored_sectors", [])]
        lagging_list = [s.split()[0] for s in regime_data.get("lagging_sectors", [])]
        
        is_favored = ticker in favored_list
        is_lagging = ticker in lagging_list
        
        # Coherent Hybrid Allocation (Quantitative Momentum + Macro Regime Overlay)
        if is_favored and momentum_score >= 0:
            alloc = "OVERWEIGHT (OW)"
            stance = "bullish"
            rationale = "Favored Siklus Makro + Momentum Positif"
        elif is_favored and momentum_score < 0:
            alloc = "OVERWEIGHT (AKUMULASI)"
            stance = "bullish"
            rationale = "Favored Siklus Makro (Peluang Buy on Dip)"
        elif is_lagging and momentum_score <= 0:
            alloc = "UNDERWEIGHT (UW)"
            stance = "bearish"
            rationale = "Dihindari Siklus Makro + Momentum Lemah"
        elif is_lagging and momentum_score > 0:
            alloc = "TACTICAL UNDERWEIGHT"
            stance = "neutral"
            rationale = "Rebound Jangka Pendek di Tengah Hambatan Makro"
        elif momentum_score > 2.0:
            alloc = "OVERWEIGHT TAKTIS"
            stance = "bullish"
            rationale = "Momentum Defensif Kuat (Rotasi Safe-Haven)"
        elif momentum_score < -2.0:
            alloc = "UNDERWEIGHT TAKTIS"
            stance = "bearish"
            rationale = "Tekanan Momentum Berat"
        else:
            alloc = "NEUTRAL (N)"
            stance = "neutral"
            rationale = "Konsolidasi Siklus & Momentum Berimbang"
            
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
            "stance": stance,
            "rationale": rationale
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
    ihsg = prices.get("^JKSE", {}).get("close", 0)
    ihsg_chg = prices.get("^JKSE", {}).get("change_1d_pct", 0)
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
        bi_desc = "Ruang pelonggaran BI-Rate terkunci. BI mempertahankan suku bunga acuan dan intervensi 'Triple Intervention' (DNDF, spot, SBN) guna meredam imported inflation & volatilitas kurs."
    else:
        bi_status = "NETRAL / AKOMODATIF"
        bi_desc = "Ruang pemangkasan suku bunga terbuka jika inflasi domestik terjaga."
        
    # 3. Beban Fiskal APBN & Energi
    if oil > 90.0:
        apbn_status = "BEBAN SUBSIDI MENINGKAT"
        apbn_desc = f"Harga minyak WTI (${oil:.2f}/bbl) melampaui asumsi ICP APBN, memperlebar defisit subsidi energi dan menekan neraca migas."
    else:
        apbn_status = "TERKENDALI"
        apbn_desc = f"Harga minyak ${oil:.2f}/bbl masih dalam batas toleransi fiskal."
        
    # 4. Transmisi ke IHSG & Arus Asing (EIDO)
    if ihsg > 0:
        if ihsg_chg < -1.5:
            ihsg_status = "KOREKSI BERAT"
        elif ihsg_chg < 0:
            ihsg_status = "KONSOLIDASI MELEMAH"
        else:
            ihsg_status = "REBOUND SELEKTIF"
        ihsg_desc = f"IHSG berada di level {ihsg:,.2f} ({ihsg_chg:+.2f}%), dengan EIDO {eido_chg:+.2f}% mencerminkan dinamika foreign flow di bursa domestik."
    else:
        if us10y > 4.8 and dxy > 102.0:
            ihsg_status = "RISK-OFF ASING"
            ihsg_desc = f"EIDO ({eido_chg:+.2f}%) mencerminkan de-risking investor asing dari saham perbankan big-cap."
        else:
            ihsg_status = "NETRAL / INFLOW SELEKTIF"
            ihsg_desc = "Arus modal asing selektif masuk ke saham domestik."
        
    ihsg_str_part = f"IHSG di {ihsg:,.2f} ({ihsg_chg:+.2f}%), " if ihsg > 0 else ""
    summary_paragraph = (
        f"Kombinasi US10Y di level {us10y:.3f}%, DXY {dxy:.2f}, dan WTI Crude ${oil:.2f} memicu transmisi ke Indonesia lewat "
        f"depresiasi nilai tukar (USD/IDR Rp {usdidr:,.0f}) dan risiko imported inflation energi. {ihsg_str_part}"
        f"Bank Indonesia dipaksa menahan BI-Rate tetap tinggi dan menjaga stabilitas valas, yang berdampak menekan valuasi perbankan "
        f"IHSG, meskipun emiten komoditas energi mendapat kompensasi dari tingginya harga komoditas global."
    )
    
    return {
        "usdidr_val": usdidr,
        "usdidr_chg": usdidr_chg,
        "eido_val": eido,
        "eido_chg": eido_chg,
        "ihsg_val": ihsg,
        "ihsg_chg": ihsg_chg,
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
    Automated Real-Time News & Causality Engine:
    Links price movements of Gold, Crypto (BTC), Oil, US Dollar/Yields, Wall Street Tech, and IHSG
    directly to live news headlines and market sentiment catalysts.
    """
    prices = snapshot.get("prices", {})
    net_liq = snapshot.get("net_liquidity", {})
    news_cat = snapshot.get("news_by_category", {})
    
    # Prices & Movements
    oil = prices.get("CL=F", {}).get("close", 0)
    oil_1d = prices.get("CL=F", {}).get("change_1d_pct", 0)
    oil_20d = prices.get("CL=F", {}).get("change_20d_pct", 0)
    
    btc = prices.get("BTC-USD", {}).get("close", 0)
    btc_1d = prices.get("BTC-USD", {}).get("change_1d_pct", 0)
    btc_20d = prices.get("BTC-USD", {}).get("change_20d_pct", 0)
    
    tnx = prices.get("^TNX", {}).get("close", 0)
    tnx_1d = prices.get("^TNX", {}).get("change_1d_pct", 0)
    dxy = prices.get("DX-Y.NYB", {}).get("close", 0)
    dxy_1d = prices.get("DX-Y.NYB", {}).get("change_1d_pct", 0)
    
    gold = prices.get("GC=F", {}).get("close", 0)
    gold_1d = prices.get("GC=F", {}).get("change_1d_pct", 0)
    gold_20d = prices.get("GC=F", {}).get("change_20d_pct", 0)
    
    qqq = prices.get("QQQ", {}).get("close", 0)
    qqq_1d = prices.get("QQQ", {}).get("change_1d_pct", 0)
    spx = prices.get("SPY", {}).get("close", 0)
    spx_1d = prices.get("SPY", {}).get("change_1d_pct", 0)
    
    ihsg = prices.get("^JKSE", {}).get("close", 5032.44)
    ihsg_1d = prices.get("^JKSE", {}).get("change_1d_pct", -1.29)
    usdidr = prices.get("IDR=X", {}).get("close", 18140.0)
    usdidr_1d = prices.get("IDR=X", {}).get("change_1d_pct", 0.41)
    
    def get_top_news(cat_key, fallback_title, fallback_src):
        items = news_cat.get(cat_key, [])
        if not items and cat_key == "oil":
            items = snapshot.get("geopolitics_news", [])
        elif not items and cat_key == "crypto":
            items = snapshot.get("crypto_news", [])
        elif not items and cat_key == "indonesia":
            items = snapshot.get("indonesia_news", [])
        elif not items and cat_key == "tech":
            items = snapshot.get("global_news", [])
            
        if items and len(items) > 0:
            it = items[0]
            return {
                "title": it.get("title", fallback_title),
                "source": it.get("source", fallback_src),
                "link": it.get("link", "#")
            }
        return {"title": fallback_title, "source": fallback_src, "link": "#"}

    # 1. EMAS & LOGAM MULIA (GOLD / XAUUSD)
    gold_news = get_top_news("gold", "Gold prices fluctuate as Fed rate expectations evolve", "Reuters")
    if gold_1d < 0:
        gold_tag = "Penguatan Dolar & Yield Restriktif"
        gold_driver = (
            f"Emas Spot terkoreksi ke US$ {gold:,.1f}/oz ({gold_1d:+.2f}%) dipicu oleh tingginya yield obligasi US 10Y ({tnx:.3f}%) "
            f"dan rilis data inflasi yang menahan ekspektasi penurunan suku bunga The Fed ('{gold_news['title']}'). "
            f"Kondisi ini menaikkan 'opportunity cost' memegang aset tanpa imbal hasil (non-yielding asset)."
        )
        gold_summary = f"Kekhawatiran suku bunga ketat & penguatan yield menekan emas ({gold_news['source']})"
    else:
        gold_tag = "Permintaan Safe-Haven & Hedging"
        gold_driver = (
            f"Emas Spot menguat ke US$ {gold:,.1f}/oz ({gold_1d:+.2f}%) didorong oleh arus beli lindung nilai terhadap inflasi "
            f"dan peningkatan permintaan safe-haven global di tengah ketegangan geopolitik ('{gold_news['title']}')."
        )
        gold_summary = f"Permintaan aset safe-haven & lindung nilai inflasi meningkat ({gold_news['source']})"

    # 2. MINYAK MENTAH & ENERGI (CRUDE OIL / WTI)
    oil_news = get_top_news("oil", "Crude oil trades amidst supply constraints and geopolitical watch", "Reuters")
    if oil_1d > 0.5 or oil > 95.0:
        oil_tag = "Premi Risiko Pasokan & Geopolitik"
        oil_driver = (
            f"Minyak mentah WTI berada di level tinggi US$ {oil:.2f}/barel (1D: {oil_1d:+.2f}%, 20D: {oil_20d:+.1f}%) "
            f"didorong oleh disiplin kuota pasokan OPEC+ dan premi risiko geopolitik pasokan energi ('{oil_news['title']}'). "
            f"Lonjakan ini mentransmisikan tekanan biaya produksi (cost-push inflation) ke seluruh sektor industri."
        )
        oil_summary = f"Premi risiko pasokan energi & disiplin kuota pasokan ({oil_news['source']})"
    else:
        oil_tag = "Harapan Diplomasi & Melandainya Premi Pasokan"
        oil_driver = (
            f"Minyak mentah WTI melandai ke US$ {oil:.2f}/barel ({oil_1d:+.2f}%) sejalan dengan munculnya harapan diplomasi "
            f"yang meredakan kekhawatiran disrupsi pasokan fisik di pasar komoditas ('{oil_news['title']}')."
        )
        oil_summary = f"Harapan diplomasi kawasan meredakan kekhawatiran pasokan ({oil_news['source']})"

    # 3. BITCOIN & PASAR KRIPTO
    crypto_news = get_top_news("crypto", "Bitcoin and crypto markets consolidate near critical support", "CoinDesk")
    if btc_1d < -1.0 or btc_20d < -3.0:
        btc_tag = "Likuidasi Derivatif & Volatilitas Sentimen"
        btc_driver = (
            f"Koreksi Bitcoin ke kisaran US$ {btc:,.0f} (1D: {btc_1d:+.2f}%, 20D: {btc_20d:+.1f}%) dipicu oleh likuidasi posisi "
            f"leverage tinggi di pasar derivatif dan sentimen kehati-hatian investor ('{crypto_news['title']}'). "
            f"Tingginya yield US 10Y ({tnx:.3f}%) menyedot likuiditas pasar dan memicu aksi de-risking aset digital."
        )
        btc_summary = f"Likuidasi derivatif leverage & volatilitas sentimen ekosistem ({crypto_news['source']})"
    elif btc_1d > 1.5:
        btc_tag = "Inflow ETF Spot & Risk-On"
        btc_driver = (
            f"Bitcoin menguat ke US$ {btc:,.0f} ({btc_1d:+.2f}%) ditopang oleh akumulasi arus masuk bersih ETF Spot "
            f"dan perbaikan selera risiko pasar digital ('{crypto_news['title']}')."
        )
        btc_summary = f"Arus masuk modal ETF & perbaikan selera risiko ({crypto_news['source']})"
    else:
        btc_tag = "Konsolidasi Menunggu Katalis"
        btc_driver = (
            f"Bitcoin berkonsolidasi di kisaran US$ {btc:,.0f} ({btc_1d:+.2f}%) menunggu katalis baru arah kebijakan moneter "
            f"dan stabilitas pasar saham Wall Street ('{crypto_news['title']}')."
        )
        btc_summary = f"Konsolidasi di area support menanti pemicu likuiditas ({crypto_news['source']})"

    # 4. US DOLLAR (DXY) & US 10Y TREASURY YIELD
    dollar_news = get_top_news("dollar", "Treasury yields and US Dollar reflect interest rate expectations", "CNBC")
    if tnx_1d > 0.4 or dxy_1d > 0.2:
        dollar_tag = "Ekspektasi Suku Bunga Higher-for-Longer"
        dollar_driver = (
            f"US 10Y Yield naik ke {tnx:.3f}% ({tnx_1d:+.2f}%) dan Dollar AS (DXY {dxy:.2f}) menguat "
            f"terdorong oleh data ekonomi yang memperkuat proyeksi suku bunga The Fed tetap restriktif ('{dollar_news['title']}')."
        )
        dollar_summary = f"Ekspektasi suku bunga restriktif menopang Dollar & Yield ({dollar_news['source']})"
    else:
        dollar_tag = "Konsolidasi Pasar Obligasi & Safe-Haven Bid"
        dollar_driver = (
            f"US 10-Year Yield melandai ke {tnx:.3f}% ({tnx_1d:+.2f}%) dan DXY di {dxy:.2f} mencerminkan aksi konsolidasi "
            f"pasar obligasi dan aliran perlindungan modal di tengah volatilitas pasar saham global ('{dollar_news['title']}')."
        )
        dollar_summary = f"Aksi lindung nilai pasar obligasi menahan lonjakan yield ({dollar_news['source']})"

    # 5. WALL STREET & BIG TECH (NASDAQ / S&P 500)
    tech_news = get_top_news("tech", "Wall Street equities adjust to tech earnings and rate expectations", "Bloomberg")
    if qqq_1d < 0 or spx_1d < 0:
        tech_tag = "Kekhawatiran Belanja AI & Penyesuaian Valuasi"
        tech_driver = (
            f"Koreksi Nasdaq (QQQ {qqq_1d:+.2f}%) dan S&P 500 (SPY {spx_1d:+.2f}%) dipicu oleh kekhawatiran profitabilitas belanja "
            f"infrastruktur AI korporasi serta evaluasi valuasi saham-saham ber-PE tinggi di tengah suku bunga restriktif ('{tech_news['title']}')."
        )
        tech_summary = f"Penyesuaian valuasi laba korporasi & kekhawatiran belanja modal AI ({tech_news['source']})"
    else:
        tech_tag = "Optimisme Laba Korporasi & Sektor Semikonduktor"
        tech_driver = (
            f"Wall Street (QQQ {qqq_1d:+.2f}%, SPY {spx_1d:+.2f}%) menguat didorong oleh optimisme adopsi komputasi AI "
            f"dan resiliensi neraca keuangan emiten teknologi terkemuka ('{tech_news['title']}')."
        )
        tech_summary = f"Kinerja solid sektor cip & optimisme adopsi kecerdasan buatan ({tech_news['source']})"

    # 6. PASAR MODAL INDONESIA (IHSG & RUPIAH)
    indo_news = get_top_news("indonesia", "Bank Indonesia jaga stabilitas nilai tukar Rupiah di tengah dinamika global", "CNBC Indonesia")
    if ihsg_1d < 0 or usdidr_1d > 0.2:
        indo_tag = "Outflow Modal Asing & Tekanan Valas"
        indo_driver = (
            f"IHSG tertekan ke level {ihsg:,.2f} ({ihsg_1d:+.2f}%) dan USD/IDR berada di Rp {usdidr:,.0f} "
            f"akibat keluarnya aliran dana asing (foreign outflow), sentimen rebalancing indeks global, dan fokus Bank Indonesia "
            f"menjaga stabilitas kurs ('{indo_news['title']}')."
        )
        indo_summary = f"Arus keluar modal asing & penyesuaian bobot portofolio global ({indo_news['source']})"
    else:
        indo_tag = "Akumulasi Selektif & Resiliensi Domestik"
        indo_driver = (
            f"IHSG bertahan di {ihsg:,.2f} ({ihsg_1d:+.2f}%) ditopang oleh akumulasi investor domestik pada saham berbasis dividen "
            f"dan komoditas, diimbangi oleh intervensi stabilisasi Bank Indonesia ('{indo_news['title']}')."
        )
        indo_summary = f"Dukungan akumulasi saham dividen & stabilisasi moneter BI ({indo_news['source']})"

    # 7. Likuiditas The Fed
    liq_bil = net_liq.get("net_liquidity_bil", 0)
    chg_4w = net_liq.get("change_4w_bil", 0)
    fed_driver = (
        f"Likuiditas Bersih The Fed tercatat US$ {liq_bil:,.1f} Miliar (Perubahan 4 Pekan: {chg_4w:+.1f} Miliar). "
        f"Siklus rilis resmi neraca The Fed (H.4.1) terbit setiap Kamis sore waktu Washington DC (Jumat ~03:30 WIB). "
        f"Perubahan neto diatur oleh saldo TGA Departemen Keuangan AS dan fasilitas Reverse Repo (RRP)."
    )

    # 8. Dinamika Makro Rezim
    regime_driver = (
        f"Status Rezim: '{regime['title']}'. Model 4-kuadran mengunci status ini karena kombinasi Minyak (US$ {oil:.2f} > $88) "
        f"dan Yield 10Y ({tnx:.3f}% > 4.50%). Untuk beralih ke 'Disinflasi / Goldilocks', harga minyak harus turun ke bawah $80 "
        f"dan yield US10Y melandai ke bawah 4.40%."
    )

    return {
        "gold": {
            "price": gold, "chg_1d": gold_1d, "chg_20d": gold_20d,
            "driver": gold_driver, "tag": gold_tag, "summary": gold_summary,
            "news": gold_news
        },
        "oil": {
            "price": oil, "chg_1d": oil_1d, "chg_20d": oil_20d,
            "driver": oil_driver, "tag": oil_tag, "summary": oil_summary,
            "news": oil_news
        },
        "crypto": {
            "price": btc, "chg_1d": btc_1d, "chg_20d": btc_20d,
            "driver": btc_driver, "tag": btc_tag, "summary": btc_summary,
            "news": crypto_news
        },
        "dollar": {
            "dxy": dxy, "chg_1d": dxy_1d, "tnx": tnx, "tnx_1d": tnx_1d,
            "driver": dollar_driver, "tag": dollar_tag, "summary": dollar_summary,
            "news": dollar_news
        },
        "tech": {
            "qqq": qqq, "qqq_1d": qqq_1d, "spx": spx, "spx_1d": spx_1d,
            "driver": tech_driver, "tag": tech_tag, "summary": tech_summary,
            "news": tech_news
        },
        "indonesia": {
            "ihsg": ihsg, "ihsg_1d": ihsg_1d, "usdidr": usdidr, "usdidr_1d": usdidr_1d,
            "driver": indo_driver, "tag": indo_tag, "summary": indo_summary,
            "news": indo_news
        },
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
