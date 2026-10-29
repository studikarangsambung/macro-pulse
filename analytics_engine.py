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
