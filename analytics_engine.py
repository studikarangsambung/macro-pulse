"""
Analytics & Quantitative Macro Engine for US Sectors and Crypto
Computes:
1. Early Warning Signals (EWS) with institutional thresholds
2. 4-Quadrant Macro Regime Classification
3. Cross-Asset Rolling Correlation Matrix (with BREAK / INVERT detection)
4. S&P 500 11 Sector & Crypto Tactical Scorecard
"""

import copy
import sqlite3
import pandas as pd
import numpy as np
from config import DB_PATH, EWS_THRESHOLDS, TICKERS_SECTORS, TICKERS_CRYPTO
import driver_engine as _driver_engine
from driver_engine import get_px, classify_move, yield_change_bp, co_phrase, liquidity_state, pct as _pct

DEFENSIVE_SECTORS = {"XLP", "XLU", "XLV"}

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
    # FIX: status no longer depends on the 10Y level (that double-counted indicator #1) and a
    #      missing ^IRX no longer produces a fake ~+490 bps slope.
    irx = prices.get("^IRX", {}).get("close")
    if tnx and irx:
        spread_10y_3m = (tnx - irx) * 100.0  # in bps
        if spread_10y_3m < 0:
            status = "WASPADA"
            ctx = f"Kurva inverted ({spread_10y_3m:.1f} bps) - sinyal historis pengetatan likuiditas dan resesi lanjutan."
        else:
            status = "AMAN"
            ctx = f"Kurva positif ({spread_10y_3m:.1f} bps), tidak inverted."
        value = f"{spread_10y_3m:+.1f} bps"
    else:
        status, ctx, value = "N/A", "Data ^TNX/^IRX tidak tersedia.", "n/a"
    signals.append({
        "name": "Yield Curve (10Y - 3M T-Bill)",
        "value": value,
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
    # FIX: percent-of-level rule shared with the broadcast (driver_engine.liquidity_state);
    #      a fixed -50bn cliff made -52.5bn "agresif" while being only ~0.9% of the balance.
    net_liq_val = net_liq.get("net_liquidity_bil", 0)
    net_liq_chg = net_liq.get("change_4w_bil", 0)
    liq_label, liq_status = liquidity_state(net_liq_val, net_liq_chg)
    if liq_status is None:
        status, ctx = "N/A", "Data likuiditas tidak tersedia."
    else:
        status = liq_status
        p = net_liq_chg / net_liq_val * 100.0
        ctx = f"Likuiditas bersih Fed {net_liq_chg:+.1f}B ({p:+.2f}% dari level) dalam 4 minggu: {liq_label.lower()}."
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
        ctx = f"Rupiah di Rp {usdidr:,.0f}, melampaui ambang psikologis Rp 18.000."
    elif usdidr > 16500:
        status = "WASPADA"
        ctx = f"Rupiah Rp {usdidr:,.0f} di zona waspada (di atas Rp 16.500)."
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
    # FIX: no absolute price threshold (was "> 3800") and no dependence on the 10Y level;
    #      status comes from the 20D move and the text states the actual direction.
    g = get_px(prices, "GC=F")
    gold = g["close"] if g else 0
    c20 = g["chg_20d"] if g else None
    if c20 is not None and abs(c20) >= 8.0:
        status = "WASPADA"
        ctx = f"Emas ${gold:,.1f}/oz bergerak {c20:+.1f}% dalam 20 hari (volatil)."
    else:
        status = "AMAN"
        ctx = f"Emas ${gold:,.1f}/oz, 20D {_pct(c20, 1)} (stabil)."
    signals.append({
        "name": "Emas (XAUUSD)",
        "value": f"${gold:,.1f}/oz",
        "status": status,
        "context": ctx
    })
    
    # FIX: a missing input used to be read as 0 (e.g. "Rupiah stabil di Rp 0", real yield 0% "akomodatif").
    _px_map = {"US 10Y Treasury Yield": "^TNX", "CBOE Volatility Index (VIX)": "^VIX",
               "US Dollar Index (DXY)": "DX-Y.NYB", "WTI Crude Oil": "CL=F",
               "USD / IDR (Kurs Rupiah)": "USDIDR=X"}
    _fred_map = {"US 10Y Real Yield (TIPS)": "DFII10", "US High Yield Credit Spread": "BAMLH0A0HYM2"}
    for s in signals:
        t = _px_map.get(s["name"])
        f = _fred_map.get(s["name"])
        if (t and not prices.get(t, {}).get("close")) or (f and fred.get(f, {}).get("value") is None):
            s.update(status="N/A", value="n/a", context="Data tidak tersedia.")
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
    # FIX: never classify on invented defaults (oil=75, vix=18, tnx=4.0 silently produced
    # "DEFLASI_KONTRAKSI" through the catch-all else-branch).
    _missing = [t for t in ("CL=F", "^TNX", "^VIX") if not prices.get(t, {}).get("close")]
    if _missing:
        return {
            "regime_id": "DATA_TIDAK_LENGKAP",
            "title": "REZIM TIDAK DAPAT DIKLASIFIKASI (DATA TIDAK LENGKAP)",
            "summary": "Input hilang: " + ", ".join(_missing) + ". Tidak ada klasifikasi yang dipaksakan.",
            "analog": "-", "favored_sectors": [], "lagging_sectors": [],
            "crypto_stance": "NETRAL / TUNGGU DATA",
            "score_bahaya": sum(1 for s in ews_signals if s["status"] == "BAHAYA"),
            "score_waspada": sum(1 for s in ews_signals if s["status"] == "WASPADA"),
        }
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

def explain_regime_exit(snapshot, ews_signals):
    """
    What-if text produced by calling classify_macro_regime itself, so the page can never
    describe transition rules that differ from the code (the old text claimed that oil < $80
    AND yield < 4.40% were needed and that the next state was "Goldilocks"; the code flips
    to REFLASI as soon as EITHER oil <= 88 OR yield <= 4.50%).
    """
    cur = classify_macro_regime(snapshot, ews_signals)
    base = ("Klasifikasi ini murni berbasis harga dan likuiditas (minyak, yield 10Y, VIX, perubahan "
            "likuiditas 4 pekan); model TIDAK memakai data pertumbuhan ekonomi. ")
    if cur["regime_id"] == "DATA_TIDAK_LENGKAP":
        return base
    prices = snapshot.get("prices", {})
    tests = []
    for label, tick, val in (("minyak turun ke US$ 88", "CL=F", 88.0),
                             ("yield 10Y turun ke 4.50%", "^TNX", 4.5)):
        px = prices.get(tick, {}).get("close")
        if px and px > val:
            snap = copy.deepcopy(snapshot)
            snap["prices"][tick]["close"] = val
            new = classify_macro_regime(snap, ews_signals)
            if new["regime_id"] != cur["regime_id"]:
                tests.append(f"jika hanya {label} -> '{new['title']}'")
    if tests:
        base += ("Uji batas: " + "; ".join(tests) +
                 ". Label berubah hanya karena satu ambang harga, bukan karena data pertumbuhan. ")
    return base


def compute_correlation_matrix(price_df, window=30):
    if price_df.empty or len(price_df) < 15:
        return []
    
    # Calculate daily returns
    # FIX: align on US equity trading days. ffill() over a 7-day crypto calendar injected
    # zero-return weekend rows for equities and distorted every correlation.
    base = price_df
    if "SPY" in base.columns:
        base = base.loc[base["SPY"].dropna().index]
    returns = base.ffill().pct_change().dropna()
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
            # FIX: only genuinely defensive sectors may be called "defensif" (XLF was mislabelled)
            rationale = ("Momentum Defensif Kuat (Rotasi Safe-Haven)" if ticker in DEFENSIVE_SECTORS
                         else "Momentum Kuat (di luar prioritas rezim)")
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
    """
    FIX: no hard-coded fallback prices (previously 18140 / 10.45 / 5032.44), no unconditional
    summary paragraph, no claims about BI actions or foreign flows that are not in the data,
    and IHSG status now looks at the 20D move too (a -16% month is not "konsolidasi").
    """
    prices = snapshot.get("prices", {})
    idr = get_px(prices, "USDIDR=X", "IDR=X")
    eido = get_px(prices, "EIDO")
    ih = get_px(prices, "^JKSE")
    tnx = get_px(prices, "^TNX")
    dxy = get_px(prices, "DX-Y.NYB")
    oil = get_px(prices, "CL=F")
    tnx_bp = yield_change_bp(tnx["close"], tnx["chg_1d"]) if tnx else None

    # 1. Rupiah
    if not idr:
        kurs_status, kurs_desc = "DATA TIDAK TERSEDIA", "Data USD/IDR tidak tersedia."
    else:
        v, c = idr["close"], idr["chg_1d"]
        kurs_status = "TEKANAN BERAT" if v > 18000 else "WASPADA" if v > 16500 else "STABIL"
        kurs_desc = f"USD/IDR Rp {v:,.0f} ({_pct(c)} 1D); ambang psikologis Rp 18.000."
        if dxy:
            co = co_phrase(classify_move("fx", c), "DXY", classify_move("dollar", dxy["chg_1d"]),
                           _pct(dxy["chg_1d"]))
            if co:
                kurs_desc += " " + co + "."

    # 2. Bank Indonesia policy room (model estimate only - no BI data is fetched)
    us10y = tnx["close"] if tnx else None
    if (us10y and us10y > 4.6) or (idr and idr["close"] > 17500):
        bi_status = "HAWKISH (estimasi model dari kurs & yield, bukan data BI)"
        bi_desc = ("Estimasi: kurs di atas Rp 17.500 dan/atau US10Y di atas 4.6% biasanya membatasi ruang "
                   "pelonggaran. Tidak memakai data BI-Rate, cadangan devisa, atau intervensi aktual.")
    else:
        bi_status = "NETRAL (estimasi model dari kurs & yield, bukan data BI)"
        bi_desc = "Estimasi: kurs dan yield belum menekan ruang kebijakan. Tidak memakai data BI aktual."

    # 3. Energy / fiscal
    if not oil:
        apbn_status, apbn_desc = "DATA TIDAK TERSEDIA", "Data minyak tidak tersedia."
    elif oil["close"] > 90.0:
        apbn_status = "TEKANAN SUBSIDI POTENSIAL"
        apbn_desc = (f"WTI US$ {oil['close']:.2f} di atas US$ 90: tekanan potensial pada subsidi energi dan "
                     "neraca migas (estimasi; asumsi ICP APBN tidak diambil dari data).")
    else:
        apbn_status = "TERKENDALI"
        apbn_desc = f"WTI US$ {oil['close']:.2f}, di bawah ambang US$ 90."

    # 4. IHSG and EIDO (each labelled from its OWN move)
    if ih:
        c1, c20 = ih["chg_1d"], ih["chg_20d"]
        if c20 is not None and c20 <= -8:
            ihsg_status = "KOREKSI DALAM (20D)"
        elif c1 is not None and c1 < -1.5:
            ihsg_status = "KOREKSI BERAT"
        elif c1 is not None and c1 < 0:
            ihsg_status = "KONSOLIDASI MELEMAH"
        else:
            ihsg_status = "REBOUND SELEKTIF"
        ihsg_desc = f"IHSG {ih['close']:,.2f} ({_pct(c1)} 1D, {_pct(c20, 1)} 20D)."
    else:
        ihsg_status, ihsg_desc = "DATA TIDAK TERSEDIA", "Data IHSG tidak tersedia."
    eido_state = classify_move("equity", eido["chg_1d"]) if eido else None
    eido_status = {"naik": "MENGUAT", "turun": "MELEMAH", "datar": "DATAR"}.get(eido_state, "DATA TIDAK TERSEDIA")

    parts = []
    if idr:
        parts.append(f"USD/IDR Rp {idr['close']:,.0f} ({_pct(idr['chg_1d'])} 1D)")
    if dxy:
        parts.append(f"DXY {dxy['close']:.2f} ({_pct(dxy['chg_1d'])})")
    if tnx:
        parts.append(f"US10Y {tnx['close']:.3f}% ({tnx_bp:+.1f} bp 1D)" if tnx_bp is not None
                     else f"US10Y {tnx['close']:.3f}%")
    if oil:
        parts.append(f"WTI US$ {oil['close']:.2f} ({_pct(oil['chg_1d'])} 1D)")
    summary_paragraph = "Indikator eksternal: " + ("; ".join(parts) if parts else "tidak tersedia") + ". "
    if ih:
        summary_paragraph += ihsg_desc + " "
    summary_paragraph += ("Penyebab pergerakan tidak dapat dipastikan dari data harga; "
                          "lihat berita terkait dan faktor domestik.")

    return {
        "usdidr_val": idr["close"] if idr else None,
        "usdidr_chg": idr["chg_1d"] if idr else None,
        "eido_val": eido["close"] if eido else None,
        "eido_chg": eido["chg_1d"] if eido else None,
        "eido_status": eido_status,
        "ihsg_val": ih["close"] if ih else None,
        "ihsg_chg": ih["chg_1d"] if ih else None,
        "ihsg_20d": ih["chg_20d"] if ih else None,
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
    Thin wrapper kept for backward compatibility with html_generator / narrative_generator.
    FIX: the old implementation picked items[0] of each news list and glued it to a
    hard-coded cause ("dipicu oleh ...") chosen only by the sign of the move (or of the
    20D move, or of the price LEVEL). All logic now lives in driver_engine:
    moves are described from data, headlines are shown as "berita terkait" only when
    relevant and tone-compatible, and nothing is invented when data/news is missing.
    """
    out = _driver_engine.analyze_market_drivers(snapshot)
    out["regime"] = {
        "title": regime["title"],
        "driver": f"Status Rezim: '{regime['title']}'. " + explain_regime_exit(snapshot, ews_signals),
    }
    return out

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
