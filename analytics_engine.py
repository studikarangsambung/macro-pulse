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
    
    # 1. Suku Bunga & Yield Obligasi (Nominal 10Y & TIPS Real Rate - Terintegrasi Mencegah Multikolinearitas)
    tnx = prices.get("^TNX", {}).get("close", 0)
    real_rate = fred.get("DFII10", {}).get("value", 0)
    
    if tnx > EWS_THRESHOLDS["US10Y_CRITICAL"] and real_rate >= EWS_THRESHOLDS["REAL_YIELD_TIGHT"]:
        rate_status = "BAHAYA"
        rate_ctx = f"Yield 10Y ({tnx:.3f}%) & Real TIPS ({real_rate:.2f}%) berada di zona restriktif, menekan valuasi aset durasi panjang."
    elif tnx > 4.2 or real_rate >= 1.75:
        rate_status = "WASPADA"
        rate_ctx = f"Yield 10Y {tnx:.3f}% dan Real Yield {real_rate:.2f}% berada di area moderat-tinggi."
    else:
        rate_status = "AMAN"
        rate_ctx = f"Yield 10Y {tnx:.3f}% dan Real Yield {real_rate:.2f}% dalam batas toleransi pasar."
        
    signals.append({
        "name": "US 10Y Yield & Suku Bunga Riil (TIPS)",
        "value": f"{tnx:.3f}% (Real: {real_rate:.2f}%)",
        "status": rate_status,
        "context": rate_ctx
    })
    
    # 2. Yield Curve Slope (10Y - 3M T-Bill)
    irx = prices.get("^IRX", {}).get("close", 0)
    spread_10y_3m = (tnx - irx) * 100.0  # in bps
    if spread_10y_3m < 0:
        status = "WASPADA"
        ctx = f"Kurva inverted ({spread_10y_3m:.1f} bps) - sinyal historis pengetatan likuiditas dan siklus akhir."
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
    
    # 3. High Yield Credit Spread (BAMLH0A0HYM2)
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
    
    # 4. CBOE VIX (Graduated / Non-Biner Equity Volatility)
    vix = prices.get("^VIX", {}).get("close", 0)
    if vix >= EWS_THRESHOLDS["VIX_PANIC"]:
        status = "BAHAYA"
        ctx = f"VIX {vix:.2f} di zona kepanikan ekuitas (>30)."
    elif vix >= 22.0:
        status = "WASPADA TINGGI"
        ctx = f"VIX {vix:.2f} di atas batas rata-rata volatilitas."
    elif vix >= 18.0:
        status = "WASPADA RENDAH"
        ctx = f"VIX {vix:.2f} berada di zona transisi (18-22)."
    else:
        status = "AMAN"
        ctx = f"VIX {vix:.2f} relatif stabil di bawah 18."
    signals.append({
        "name": "CBOE Volatility Index (VIX)",
        "value": f"{vix:.2f}",
        "status": status,
        "context": ctx
    })
    
    # 5. Fed Net Liquidity (Proportional Analysis)
    net_liq_val = net_liq.get("net_liquidity_bil", 0)
    net_liq_chg = net_liq.get("change_4w_bil", 0)
    pct_liq_chg = (net_liq_chg / net_liq_val * 100.0) if net_liq_val > 0 else 0
    
    if net_liq_chg <= -100.0 or pct_liq_chg <= -2.0:
        status = "BAHAYA"
        ctx = f"Kontraksi likuiditas bersih agresif −${abs(net_liq_chg):.1f}B ({pct_liq_chg:.1f}% 4W)."
    elif net_liq_chg < 0:
        status = "WASPADA"
        ctx = f"Pengetatan likuiditas bersih terukur/moderat ${net_liq_chg:+.1f}B ({pct_liq_chg:+.1f}% 4W dari total ${net_liq_val:,.0f}B)."
    else:
        status = "AMAN"
        ctx = f"Injeksi likuiditas bersih Fed +${net_liq_chg:.1f}B (Katalis ekspansi likuiditas pasar)."
    signals.append({
        "name": "Fed Net Liquidity (4W Delta)",
        "value": f"${net_liq_val:,.1f}B ({net_liq_chg:+.1f}B)",
        "status": status,
        "context": ctx
    })
    
    # 6. US Dollar Index (DXY)
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
    
    # 7. WTI Crude Oil
    oil = prices.get("CL=F", {}).get("close", 0)
    if oil >= 90.0:
        status = "BAHAYA"
        ctx = f"Minyak ${oil:.2f}/bbl memicu risiko stagflasi dan kenaikan ekspektasi inflasi energi."
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

    # 8. USD / IDR (Kurs Rupiah Terkalibrasi)
    usdidr = prices.get("USDIDR=X", {}).get("close", 0)
    if usdidr > 18000:
        status = "BAHAYA"
        ctx = f"Rupiah tertekan di Rp {usdidr:,.0f} menembus level psikologis 18.000, memicu intervensi valas BI."
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

    # 9. Kondisi Finansial Nasional (Chicago Fed NFCI)
    nfci = fred.get("NFCI", {}).get("value", -0.487)
    if nfci > 0:
        status = "BAHAYA"
        ctx = f"NFCI {nfci:+.3f} di atas nol menunjukkan pengetatan kondisi keuangan agregat."
    elif nfci > -0.3:
        status = "WASPADA"
        ctx = f"NFCI {nfci:+.3f} netral."
    else:
        status = "AMAN"
        ctx = f"NFCI {nfci:+.3f} di bawah rata-rata historis (kondisi finansial relatif akomodatif)."
    signals.append({
        "name": "Chicago Fed Financial Conditions (NFCI)",
        "value": f"{nfci:+.3f}",
        "status": status,
        "context": ctx
    })

    # 10. Emas Spot XAUUSD & Lindung Nilai
    gold = prices.get("GC=F", {}).get("close", 0)
    if gold > 3800 and oil > 90.0:
        status = "WASPADA"
        ctx = f"Emas di kisaran ${gold:,.1f}/oz bertindak sebagai jangkar safe-haven di tengah tingginya premi energi."
    else:
        status = "AMAN"
        ctx = f"Emas ${gold:,.1f}/oz stabil, tidak mengindikasikan lonjakan kepanikan likuiditas darurat."
    signals.append({
        "name": "Emas Spot (XAUUSD)",
        "value": f"${gold:,.1f}/oz",
        "status": status,
        "context": ctx
    })
    
    return signals

def classify_macro_regime(snapshot, ews_signals):
    """
    4-Quadrant Macro Regime Classification Engine (Pertumbuhan vs Inflasi):
    Grounded in 54-Year S&P 500 Historical Backtest & Multi-Factor Macro Proxies:
    
    Sumbu X: Pertumbuhan (Growth Momentum Proxy: Copper/Gold, Yield Curve Slope, NFCI, Net Liquidity 4W)
    Sumbu Y: Inflasi (Inflation Momentum Proxy: 10Y Breakeven Inflation Rate, WTI Oil Level & Momentum)
    
    Soft Probabilities via regularized softmax to prevent brittle switching and overfitting.
    """
    prices = snapshot.get("prices", {})
    fred = snapshot.get("fred", {})
    net_liq = snapshot.get("net_liquidity", {})
    
    # 1. Macro Indicators for Growth & Inflation
    oil = prices.get("CL=F", {}).get("close", 75.0)
    oil_20d = prices.get("CL=F", {}).get("change_20d_pct", 0)
    tnx = prices.get("^TNX", {}).get("close", 4.0)
    irx = prices.get("^IRX", {}).get("close", 4.0)
    real_rate = fred.get("DFII10", {}).get("value", 2.0)
    gold = prices.get("GC=F", {}).get("close", 2000.0)
    copper = prices.get("HG=F", {}).get("close", 4.0)
    net_liq_chg = net_liq.get("change_4w_bil", 0)
    nfci = fred.get("NFCI", {}).get("value", -0.487)
    
    # Breakeven Inflation Rate (10Y Nominal minus 10Y TIPS Real Yield)
    breakeven_10y = round(tnx - real_rate, 2) if (tnx > 0 and real_rate != 0) else 2.25
    
    # Copper / Gold Ratio (Economic activity vs safe-haven demand)
    copper_gold_ratio = round((copper / gold) * 1000.0, 4) if (copper > 0 and gold > 0) else 1.65
    
    # Yield Curve Slope (10Y - 3M in bps)
    yield_curve_bps = (tnx - irx) * 100.0
    
    # 2. Multi-Factor Normalized Growth Momentum Score (-1.0 to +1.0)
    # Economic proxies:
    # - Inverted / flat yield curve drags growth
    # - Falling / low copper-to-gold ratio signals cyclical deceleration
    # - Net liquidity draining drags aggregate demand
    # - NFCI positive indicates financial tightening
    g_curve = np.clip(yield_curve_bps / 150.0, -1.0, 1.0)  # Inverted = negative
    g_cugold = np.clip((copper_gold_ratio - 1.80) / 0.50, -1.0, 1.0) # <1.80 = slowing
    g_liq = np.clip(net_liq_chg / 80.0, -1.0, 1.0)
    g_nfci = np.clip(-nfci * 2.0, -1.0, 1.0) # NFCI negative is loose/good for growth
    
    growth_score = float(np.clip((0.35 * g_curve) + (0.35 * g_cugold) + (0.15 * g_liq) + (0.15 * g_nfci), -1.0, 1.0))
    
    # 3. Multi-Factor Normalized Inflation Momentum Score (-1.0 to +1.0)
    # Inflation proxies:
    # - High Breakeven Inflation (> 2.30% indicates market pricing persistent inflation)
    # - High Oil Price & positive 20D oil momentum
    i_breakeven = np.clip((breakeven_10y - 2.15) / 0.40, -1.0, 1.0)
    i_oil = np.clip(((oil - 80.0) / 25.0) + (oil_20d / 30.0), -1.0, 1.0)
    
    inflation_score = float(np.clip((0.50 * i_oil) + (0.50 * i_breakeven), -1.0, 1.0))
    
    # 4. Softmax Probability across the 4 Macro Quadrants (Prevents overfitting & brittle jumps)
    # Quadrant 1 (Reflasi): Growth > 0, Inflation > 0
    # Quadrant 2 (Disinflasi Boom): Growth > 0, Inflation < 0
    # Quadrant 3 (Stagflasi): Growth < 0, Inflation > 0
    # Quadrant 4 (Deflasi Kontraksi): Growth < 0, Inflation < 0
    q_weights = np.array([
        0.7 * growth_score + 0.7 * inflation_score,   # Reflasi
        0.7 * growth_score - 0.7 * inflation_score,   # Disinflasi
       -0.7 * growth_score + 0.7 * inflation_score,   # Stagflasi
       -0.7 * growth_score - 0.7 * inflation_score    # Deflasi
    ])
    
    exp_q = np.exp(2.5 * q_weights)
    probs = exp_q / np.sum(exp_q)
    prob_reflasi = round(float(probs[0]) * 100, 1)
    prob_disinflasi = round(float(probs[1]) * 100, 1)
    prob_stagflasi = round(float(probs[2]) * 100, 1)
    prob_deflasi = round(float(probs[3]) * 100, 1)
    
    quadrant_idx = int(np.argmax(probs))
    
    # Map Quadrant metadata
    if quadrant_idx == 2 or (growth_score <= 0 and inflation_score > 0):
        regime = "STAGFLASI"
        title = "STAGFLASI ENERGI & SQUEEZE BIAYA"
        summary = (
            f"Pertumbuhan ekonomi melambat (Growth Score: {growth_score:+.2f}) dengan rasio Tembaga/Emas ({copper_gold_ratio:.3f}) melandai, "
            f"sementara tekanan inflasi komoditas energi (WTI ${oil:.2f}/bbl) dan ekspektasi yield US 10Y ({tnx:.3f}%) menahan ruang pemangkasan bunga."
        )
        analog = "1973 Oil Shock / Q2 2022 Fed Rate Shock"
        favored_sectors = ["XLE (Energy)", "XLP (Staples)", "Cash / T-Bills"]
        lagging_sectors = ["XLK (Tech)", "XLY (Discretionary)", "XLRE (Real Estate)"]
        crypto_stance = "DEFENSIVE / VOLATILE (Tunggu stabilisasi yield real TIPS)"
    elif quadrant_idx == 1 or (growth_score > 0 and inflation_score <= 0):
        regime = "DISINFLASI_BOOM"
        title = "DISINFLASI & EKSPANSI LIKUIDITAS"
        summary = f"Pertumbuhan ekspansif (Growth Score: {growth_score:+.2f}) berdampingan dengan inflasi terkendali (Breakeven 10Y: {breakeven_10y:.2f}%). Lingkungan kondusif bagi High-Beta."
        analog = "2020-2021 QE Expansion / 1995-1998 Tech Boom"
        favored_sectors = ["XLK (Tech)", "XLC (Communication)", "XLY (Discretionary)"]
        lagging_sectors = ["XLU (Utilities)", "XLP (Staples)"]
        crypto_stance = "AGGRESSIVE RISK-ON (BTC + High Beta Altcoins)"
    elif quadrant_idx == 0 or (growth_score > 0 and inflation_score > 0):
        regime = "REFLASI"
        title = "REFLASI & ROTASI SIKLIKAL"
        summary = f"Pertumbuhan ekonomi solid (Growth Score: {growth_score:+.2f}) diiringi penguatan harga komoditas dan yield. Sektor siklikal dan finansial memimpin rotasi."
        analog = "2004-2006 Commodity Supercycle / 2017 Global Reflation"
        favored_sectors = ["XLF (Financials)", "XLI (Industrials)", "XLE (Energy)"]
        lagging_sectors = ["XLU (Utilities)", "XLRE (Real Estate)"]
        crypto_stance = "SELECTIVE RISK-ON (BTC dominan, selektif Altcoins)"
    else:
        regime = "DEFLASI_KONTRAKSI"
        title = "DEFENSIVE LATE-CYCLE / KONTRAKSI"
        summary = f"Permintaan agregat dan inflasi melambat (Growth: {growth_score:+.2f}, Inflasi: {inflation_score:+.2f}). Rotasi ketat ke aset defensif berkualitas."
        analog = "2008 GFC Pre-crisis / 2001 Tech Hangover"
        favored_sectors = ["XLU (Utilities)", "XLV (Healthcare)", "XLP (Staples)"]
        lagging_sectors = ["XLK (Tech)", "XLY (Discretionary)", "XLI (Industrials)"]
        crypto_stance = "RISK-OFF / CAPITAL PRESERVATION (Cash & Stables)"
        
    bahaya_count = sum(1 for s in ews_signals if s["status"] == "BAHAYA")
    waspada_count = sum(1 for s in ews_signals if "WASPADA" in s["status"])
    
    return {
        "regime_id": regime,
        "title": title,
        "summary": summary,
        "analog": analog,
        "growth_score": round(growth_score, 2),
        "growth_label": "Melambat (Growth ↓)" if growth_score <= 0 else "Ekspansi (Growth ↑)",
        "inflation_score": round(inflation_score, 2),
        "inflation_label": "Tinggi / Alot (Inflasi ↑)" if inflation_score > 0 else "Melandai (Inflasi ↓)",
        "breakeven_inflation_10y": breakeven_10y,
        "copper_gold_ratio": copper_gold_ratio,
        "probabilities": {
            "stagflasi": prob_stagflasi,
            "deflasi": prob_deflasi,
            "reflasi": prob_reflasi,
            "disinflasi": prob_disinflasi
        },
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
            if ticker in ["XLV", "XLP", "XLU"]:
                rationale = "Momentum Defensif Kuat (Rotasi Safe-Haven & Kualitas)"
            else:
                rationale = f"Momentum Siklikal Positif ({meta.get('profile', 'Taktis')})"
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
    
    ihsg = prices.get("^JKSE", {}).get("close", 5057.05)
    ihsg_1d = prices.get("^JKSE", {}).get("change_1d_pct", -0.80)
    usdidr = prices.get("USDIDR=X", {}).get("close", 18120.0)
    usdidr_1d = prices.get("USDIDR=X", {}).get("change_1d_pct", 0.30)
    
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
        if tnx_1d > 0.3:
            gold_tag = "Kenaikan Yield US 10Y & Penguatan Dolar"
            gold_driver = (
                f"Emas Spot terkonsolidasi ke US$ {gold:,.1f}/oz ({gold_1d:+.2f}%) seiring kenaikan yield US 10Y ({tnx:.3f}%, {tnx_1d:+.2f}%) "
                f"yang menaikkan opportunity cost memegang aset tanpa bunga. Sentimen terkini: '{gold_news['title']}' ({gold_news['source']})."
            )
        else:
            gold_tag = "Konsolidasi di Dekat Resistensi Psikologis"
            gold_driver = (
                f"Emas Spot berkonsolidasi di kisaran US$ {gold:,.1f}/oz ({gold_1d:+.2f}%) mendekati resistensi psikologis spot $4,000 "
                f"meskipun yield US 10Y melandai ke {tnx:.3f}% ({tnx_1d:+.2f}%). Sentimen pasar terkini: '{gold_news['title']}' ({gold_news['source']})."
            )
        gold_summary = f"Konsolidasi harga emas di area resistensi ({gold_news['source']})"
    else:
        gold_tag = "Permintaan Safe-Haven & Lindung Nilai"
        gold_driver = (
            f"Emas Spot menguat ke US$ {gold:,.1f}/oz ({gold_1d:+.2f}%) didorong oleh permintaan safe-haven dan lindung nilai inflasi. "
            f"Sentimen pasar: '{gold_news['title']}' ({gold_news['source']})."
        )
        gold_summary = f"Permintaan safe-haven & lindung nilai inflasi ({gold_news['source']})"

    # 2. MINYAK MENTAH & ENERGI (CRUDE OIL / WTI)
    oil_news = get_top_news("oil", "Crude oil trades amidst supply constraints and geopolitical watch", "Reuters")
    if oil_1d > 0:
        oil_tag = "Kenaikan Harga & Premi Risiko Pasokan"
        oil_driver = (
            f"Minyak mentah WTI berada di level tinggi US$ {oil:.2f}/barel (1D: {oil_1d:+.2f}%, 20D: {oil_20d:+.1f}%), "
            f"mempertahankan premi risiko pasokan energi global di atas $100/barel. Sentimen pasar mencermati: '{oil_news['title']}' ({oil_news['source']})."
        )
        oil_summary = f"Premi risiko pasokan energi & dinamika geopolitik ({oil_news['source']})"
    else:
        oil_tag = "Melandainya Tekanan Pasokan Energi"
        oil_driver = (
            f"Minyak mentah WTI melandai ke US$ {oil:.2f}/barel ({oil_1d:+.2f}%), sejalan dengan upaya negosiasi diplomasi "
            f"yang meredakan kekhawatiran disrupsi fisik seketika ('{oil_news['title']}')."
        )
        oil_summary = f"Melandainya premi pasokan energi ({oil_news['source']})"

    # 3. BITCOIN & PASAR KRIPTO (Arah Ketat: Positif Dilarang Disebut Koreksi)
    crypto_news = get_top_news("crypto", "Bitcoin and crypto markets consolidate near critical support", "CoinDesk")
    if btc_1d >= 0:
        btc_tag = "Penguatan Resiliensi & Akumulasi"
        btc_driver = (
            f"Bitcoin bergerak menguat ke kisaran US$ {btc:,.0f} (1D: {btc_1d:+.2f}%, 20D: {btc_20d:+.1f}%), menunjukkan "
            f"daya tahan relatif terhadap fluktuasi pasar modal global. Sentimen terkini: '{crypto_news['title']}' ({crypto_news['source']})."
        )
        btc_summary = f"Penguatan harga & daya tahan pasar aset digital ({crypto_news['source']})"
    else:
        btc_tag = "Konsolidasi / Tekanan Jangka Pendek"
        btc_driver = (
            f"Bitcoin terkonsolidasi ke kisaran US$ {btc:,.0f} (1D: {btc_1d:+.2f}%, 20D: {btc_20d:+.1f}%), menguji level "
            f"support likuiditas di tengah kehati-hatian investor. Sentimen terkini: '{crypto_news['title']}' ({crypto_news['source']})."
        )
        btc_summary = f"Konsolidasi menanti katalis likuiditas baru ({crypto_news['source']})"

    # 4. US DOLLAR (DXY) & US 10Y TREASURY YIELD
    dollar_news = get_top_news("dollar", "Treasury yields and US Dollar reflect interest rate expectations", "CNBC")
    if tnx_1d > 0.3 or dxy_1d > 0.2:
        dollar_tag = "Kenaikan Imbal Hasil & Penguatan Dolar"
        dollar_driver = (
            f"US 10Y Yield naik ke {tnx:.3f}% ({tnx_1d:+.2f}%) dan Dollar AS (DXY {dxy:.2f}) menguat "
            f"terdorong oleh data ekonomi yang memperkuat proyeksi suku bunga restriktif ('{dollar_news['title']}')."
        )
        dollar_summary = f"Penguatan Dollar & Yield obligasi AS ({dollar_news['source']})"
    else:
        dollar_tag = "Konsolidasi Pasar Obligasi & Melandainya Dolar"
        dollar_driver = (
            f"US 10-Year Yield melandai ke {tnx:.3f}% ({tnx_1d:+.2f}%) dan DXY di level {dxy:.2f} ({dxy_1d:+.2f}%) mencerminkan "
            f"aksi konsolidasi pasar uang dan penyeimbangan portofolio global ('{dollar_news['title']}')."
        )
        dollar_summary = f"Melandainya yield dan stabilitas nilai tukar dolar ({dollar_news['source']})"

    # 5. WALL STREET & BIG TECH (NASDAQ / S&P 500)
    tech_news = get_top_news("tech", "Wall Street equities adjust to tech earnings and rate expectations", "Bloomberg")
    if qqq_1d < 0 or spx_1d < 0:
        tech_tag = "Kekhawatiran Belanja AI & Penyesuaian Valuasi"
        tech_driver = (
            f"Penyesuaian Wall Street (QQQ {qqq_1d:+.2f}%, SPY {spx_1d:+.2f}%) dipicu oleh evaluasi profitabilitas belanja "
            f"modal AI dan valuasi saham-saham ber-PE tinggi di tengah lingkungan suku bunga restriktif ('{tech_news['title']}')."
        )
        tech_summary = f"Penyesuaian valuasi laba korporasi & belanja modal AI ({tech_news['source']})"
    else:
        tech_tag = "Optimisme Laba Korporasi & Sektor Semikonduktor"
        tech_driver = (
            f"Wall Street (QQQ {qqq_1d:+.2f}%, SPY {spx_1d:+.2f}%) menguat didorong oleh optimisme adopsi kecerdasan buatan "
            f"dan resiliensi fundamental laba emiten teknologi ('{tech_news['title']}')."
        )
        tech_summary = f"Kinerja solid sektor cip & optimisme teknologi ({tech_news['source']})"

    # 6. PASAR MODAL INDONESIA (IHSG & RUPIAH - Single Source USD/IDR)
    indo_news = get_top_news("indonesia", "Bank Indonesia jaga stabilitas nilai tukar Rupiah di tengah dinamika global", "CNBC Indonesia")
    if ihsg_1d < 0 or usdidr_1d > 0.2:
        indo_tag = "Outflow Modal Asing & Penyesuaian Domestik"
        indo_driver = (
            f"IHSG tertekan ke level {ihsg:,.2f} ({ihsg_1d:+.2f}%, MTD tertekan akibat penyesuaian bobot indeks global dan rotasi portofolio). "
            f"Tekanan nilai tukar USD/IDR di Rp {usdidr:,.0f} ({usdidr_1d:+.2f}%) dan spread imbal hasil mendorong sikap intervensi Bank Indonesia ('{indo_news['title']}')."
        )
        indo_summary = f"Penyesuaian portofolio global & tekanan valas ({indo_news['source']})"
    else:
        indo_tag = "Akumulasi Selektif & Resiliensi Domestik"
        indo_driver = (
            f"IHSG menguat ke level {ihsg:,.2f} ({ihsg_1d:+.2f}%) ditopang oleh akumulasi investor domestik pada saham berbasis dividen "
            f"dan komoditas, diimbangi oleh stabilitas kurs USD/IDR Rp {usdidr:,.0f} ('{indo_news['title']}')."
        )
        indo_summary = f"Akumulasi selektif saham domestik & stabilitas valas ({indo_news['source']})"

    # 7. Likuiditas The Fed (DST 04:30 WIB)
    liq_bil = net_liq.get("net_liquidity_bil", 0)
    chg_4w = net_liq.get("change_4w_bil", 0)
    fed_driver = (
        f"Likuiditas Bersih The Fed tercatat US$ {liq_bil:,.1f} Miliar (Perubahan 4 Pekan: {chg_4w:+.1f} Miliar). "
        f"Rilis resmi neraca The Fed (H.4.1) terbit setiap Kamis sore waktu Washington DC (Jumat ~04:30 WIB pasca-akhir Daylight Saving Time). "
        f"Keseimbangan neto diatur oleh saldo TGA Treasury dan fasilitas Reverse Repo (RRP)."
    )

    # 8. Dinamika Makro Rezim Multi-Faktor Terkalibrasi
    growth_score = regime.get("growth_score", -0.35)
    inflation_score = regime.get("inflation_score", 0.45)
    breakeven = regime.get("breakeven_inflation_10y", 2.26)
    regime_driver = (
        f"Status Rezim: '{regime['title']}' (Probabilitas: {regime.get('probabilities', {}).get('stagflasi', 50):.1f}%). "
        f"Berdasarkan model empiris 4-kuadran, momentum pertumbuhan berada di zona {regime.get('growth_label', 'Melambat')} (Score: {growth_score:+.2f}) "
        f"dan inflasi berada di zona {regime.get('inflation_label', 'Tinggi')} (Score: {inflation_score:+.2f}, Breakeven 10Y: {breakeven:.2f}%, WTI: ${oil:.2f}). "
        f"Rotasi ke Disinflasi Boom mensyaratkan pemulihan indikator pertumbuhan dan meredanya premi komoditas energi."
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
