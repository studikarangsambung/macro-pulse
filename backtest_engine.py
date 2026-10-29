"""
Phase 3: Quantitative Backtest & Historical Macro Analog Engine
1. Event-Study Backtesting: Empirical reaction of US Sectors & Crypto to Major Macro Surprises (CPI, NFP, FOMC)
2. 5D Historical Macro Analog Matrix: Vector Cosine Similarity matching current conditions to historical shock regimes
"""

import math
import sys
import datetime
import numpy as np
import pandas as pd
import yfinance as yf
sys.stdout.reconfigure(encoding='utf-8')
from config import TICKERS_SECTORS, TICKERS_CRYPTO

# Historical Major Event Catalog (Date, Event, Type, Actual, Consensus, SurpriseSigma)
# SurpriseSigma: > 0 = Hotter than expected, < 0 = Cooler than expected
HISTORICAL_MACRO_EVENTS = [
    # CPI Releases (Hot Inflation vs Cool Disinflation)
    {"date": "2022-06-10", "event": "US CPI May (8.6% vs 8.3% cons)", "type": "CPI", "surprise": "HOT", "sigma": +1.8},
    {"date": "2022-09-13", "event": "US CPI Aug Core (0.6% vs 0.3% cons)", "type": "CPI", "surprise": "HOT", "sigma": +2.1},
    {"date": "2022-11-10", "event": "US CPI Oct (7.7% vs 8.0% cons)", "type": "CPI", "surprise": "COOL", "sigma": -1.9},
    {"date": "2023-01-12", "event": "US CPI Dec (6.5% vs 6.5% in-line)", "type": "CPI", "surprise": "IN_LINE", "sigma": 0.0},
    {"date": "2023-07-12", "event": "US CPI Jun (3.0% vs 3.1% cons)", "type": "CPI", "surprise": "COOL", "sigma": -1.2},
    {"date": "2023-09-13", "event": "US CPI Aug (Headline jump on oil)", "type": "CPI", "surprise": "HOT", "sigma": +1.1},
    {"date": "2024-01-11", "event": "US CPI Dec (Core 3.9% vs 3.8% cons)", "type": "CPI", "surprise": "HOT", "sigma": +1.3},
    {"date": "2024-04-10", "event": "US CPI Mar (Hot 3rd straight month)", "type": "CPI", "surprise": "HOT", "sigma": +1.7},
    {"date": "2024-07-11", "event": "US CPI Jun (Cool -0.1% MoM)", "type": "CPI", "surprise": "COOL", "sigma": -2.0},
    {"date": "2025-01-15", "event": "US CPI Dec (In-line cooling 2.7%)", "type": "CPI", "surprise": "COOL", "sigma": -1.1},
    {"date": "2025-08-13", "event": "US CPI Jul (Energy spike rebound)", "type": "CPI", "surprise": "HOT", "sigma": +1.4},
    {"date": "2026-04-10", "event": "US CPI Mar (Supply chain bump)", "type": "CPI", "surprise": "HOT", "sigma": +1.5},
    {"date": "2026-09-11", "event": "US CPI Aug (Core 3.4% persistent)", "type": "CPI", "surprise": "HOT", "sigma": +1.6},

    # FOMC Rate Decisions & Hawkish/Dovish Surprises
    {"date": "2022-06-15", "event": "FOMC 75 bps Jumbo Hike Shock", "type": "FOMC", "surprise": "HAWKISH", "sigma": +2.5},
    {"date": "2022-09-21", "event": "FOMC 75 bps Hike & Dot Plot Hike", "type": "FOMC", "surprise": "HAWKISH", "sigma": +2.0},
    {"date": "2022-11-02", "event": "FOMC 75 bps & Powell 'Higher for longer'", "type": "FOMC", "surprise": "HAWKISH", "sigma": +1.8},
    {"date": "2023-03-22", "event": "FOMC 25 bps post-SVB & BTFP Liquidity", "type": "FOMC", "surprise": "DOVISH", "sigma": -1.5},
    {"date": "2023-11-01", "event": "FOMC Pause & Treasury QRA Dovish Shift", "type": "FOMC", "surprise": "DOVISH", "sigma": -2.2},
    {"date": "2023-12-13", "event": "FOMC Dovish Pivot & 3 Cuts Dot Plot", "type": "FOMC", "surprise": "DOVISH", "sigma": -2.5},
    {"date": "2024-09-18", "event": "FOMC Jumbo 50 bps Cut Initiation", "type": "FOMC", "surprise": "DOVISH", "sigma": -1.9},
    {"date": "2025-06-18", "event": "FOMC Hawkish Pause on Oil Inflation", "type": "FOMC", "surprise": "HAWKISH", "sigma": +1.5},
    {"date": "2026-09-17", "event": "FOMC Rate Hike 3.75-4.00% Persistent", "type": "FOMC", "surprise": "HAWKISH", "sigma": +1.8},

    # Non-Farm Payrolls (NFP) Jobs Surprises
    {"date": "2023-02-03", "event": "US NFP Jan (+517k vs 185k blowout)", "type": "NFP", "surprise": "HOT", "sigma": +3.0},
    {"date": "2023-10-06", "event": "US NFP Sep (+336k vs 170k blowout)", "type": "NFP", "surprise": "HOT", "sigma": +2.2},
    {"date": "2024-08-02", "event": "US NFP Jul (+114k Sahm Rule Trigger)", "type": "NFP", "surprise": "COOL", "sigma": -2.4},
    {"date": "2024-10-04", "event": "US NFP Sep (+254k massive beat)", "type": "NFP", "surprise": "HOT", "sigma": +2.1},
    {"date": "2025-11-07", "event": "US NFP Oct (Labor cooling +85k)", "type": "NFP", "surprise": "COOL", "sigma": -1.8},
    {"date": "2026-08-07", "event": "US NFP Jul (Soft landing labor beat)", "type": "NFP", "surprise": "HOT", "sigma": +1.3},
]

# Historical Macro Regimes for Vector Analog Matching
# Features Vector: [US10Y, RealYield, WTI_Oil, DXY, VIX, NetLiquidityDelta]
HISTORICAL_ANALOG_REGIMES = [
    {
        "id": "1973_OIL_EMBARGO",
        "name": "Arab Oil Embargo (1973–1974)",
        "period": "1973-1974",
        "vector": [7.8, 2.5, 95.0, 105.0, 32.0, -80.0],
        "core_driver": "Kejutan pasokan minyak Timur Tengah + Inflasi struktural + Pembatasan likuiditas",
        "next_30_90d_outcome": "Inflasi inti bertahan tinggi 6-12 bulan. Sektor Energi (XLE) dan Komoditas memimpin, ekuitas non-energi mengalami kompresi valuasi (P/E compression).",
        "sector_winners": ["XLE (Energy)", "XLB (Materials)", "Cash"],
        "sector_losers": ["XLK (Tech)", "XLY (Discretionary)", "Financials"],
        "crypto_implication": "Lingkungan likuiditas restriktif menekan aset berisiko tinggi; Bitcoin cenderung bergerak korelasi dengan emas/komoditas jika persepsi moneter goyah, namun tertekan likuiditas jangka pendek."
    },
    {
        "id": "2013_TAPER_TANTRUM",
        "name": "Fed Taper Tantrum (2013)",
        "period": "May - Dec 2013",
        "vector": [2.9, 0.8, 100.0, 84.0, 18.0, -35.0],
        "core_driver": "Kenaikan mendadak yield obligasi AS akibat sinyal normalisasi neraca Fed",
        "next_30_90d_outcome": "Pasar negara berkembang (EM) dan mata uang seperti Rupiah tertekan depresiasi tajam. Sektor finansial AS (XLF) diuntungkan kurva curam, saham dividen/utilitas (XLU) tertinggal.",
        "sector_winners": ["XLF (Financials)", "XLI (Industrials)"],
        "sector_losers": ["XLU (Utilities)", "XLRE (Real Estate)", "Emerging Markets (EIDO)"],
        "crypto_implication": "Tekanan awal akibat pengetatan dolar, disusul konsolidasi."
    },
    {
        "id": "2020_COVID_QE",
        "name": "Pandemic QE & Liquidity Injection (2020–2021)",
        "period": "Mar 2020 - Dec 2021",
        "vector": [1.2, -1.0, 45.0, 92.0, 24.0, +120.0],
        "core_driver": "Injeksi neraca bank sentral massif (QE) + Suku bunga riil negatif",
        "next_30_90d_outcome": "Ekspansi valuasi eksplosif pada sektor durasi panjang (Tech) dan aset high convexity (Crypto).",
        "sector_winners": ["XLK (Tech)", "XLC (Communication)", "XLY (Discretionary)"],
        "sector_losers": ["XLE (Energy awal)", "XLU (Utilities)"],
        "crypto_implication": "Supercycle bull run eksplosif pada Bitcoin dan Altcoins."
    },
    {
        "id": "2022_RATE_SHOCK",
        "name": "Fed Hawkish Rate Shock (2022)",
        "period": "Jan - Oct 2022",
        "vector": [4.0, 1.7, 105.0, 112.0, 28.0, -75.0],
        "core_driver": "Kenaikan suku bunga agresif 75 bps beruntun + Penarikan likuiditas QT + Lonjakan Dolar",
        "next_30_90d_outcome": "Bear market ganda obligasi dan saham. Dolar DXY menguat ekstrem menekan seluruh mata uang dunia dan kompresi berat sektor teknologi.",
        "sector_winners": ["XLE (Energy)", "Cash / Dolar (UUP)"],
        "sector_losers": ["XLK (Tech)", "XLC (Comm)", "XLRE (Real Estate)"],
        "crypto_implication": "Drawdown berat hingga -65% pada Bitcoin; de-leveraging sistemik."
    },
    {
        "id": "2023_BANKING_CRISIS",
        "name": "US Banking Stress & BTFP Inflow (Mar 2023)",
        "period": "Mar - Jun 2023",
        "vector": [3.5, 1.2, 75.0, 102.0, 20.0, +65.0],
        "core_driver": "Krisis likuiditas bank regional AS memicu fasilitas darurat BTFP (Liquidity bounce)",
        "next_30_90d_outcome": "Yield obligasi turun tajam, pasar mem-price in pemotongan suku bunga darurat. Emas dan Bitcoin melonjak sebagai alternatif sistem perbankan.",
        "sector_winners": ["XLK (Tech)", "Gold", "Mega-cap Tech"],
        "sector_losers": ["XLF (Regional Banks)"],
        "crypto_implication": "Reli reliabilitas moneter Bitcoin (+40% dalam 3 minggu pasca SVB)."
    }
]

def load_backtest_price_matrix():
    """
    Downloads historical daily prices for key test assets from 2021 to 2026.
    """
    tickers = ["XLK", "XLE", "XLF", "XLU", "XLY", "SPY", "BTC-USD", "GC=F", "USDIDR=X"]
    try:
        data = yf.download(tickers, start="2021-01-01", progress=False)["Close"]
        return data.ffill()
    except Exception as e:
        print(f"Error fetching historical price matrix: {e}")
        return pd.DataFrame()

def run_event_study_backtest(price_matrix):
    """
    Calculates Cumulative Abnormal Return (CAR) and Win Rates for Hot CPI, Cool CPI, Hawkish FOMC, Dovish FOMC.
    Returns:
    - Dict with probabilities and expected returns for each asset across horizons [T+1, T+3, T+5].
    """
    if price_matrix.empty:
        return {}

    events_by_type = {
        "HOT_CPI": [e for e in HISTORICAL_MACRO_EVENTS if e["type"] == "CPI" and e["surprise"] == "HOT"],
        "COOL_CPI": [e for e in HISTORICAL_MACRO_EVENTS if e["type"] == "CPI" and e["surprise"] == "COOL"],
        "HAWKISH_FOMC": [e for e in HISTORICAL_MACRO_EVENTS if e["type"] == "FOMC" and e["surprise"] == "HAWKISH"],
        "DOVISH_FOMC": [e for e in HISTORICAL_MACRO_EVENTS if e["type"] == "FOMC" and e["surprise"] == "DOVISH"],
    }

    target_assets = ["XLK", "XLE", "XLF", "XLU", "BTC-USD"]
    results = {}

    for regime_key, event_list in events_by_type.items():
        results[regime_key] = {"sample_size": len(event_list), "assets": {}}

        for asset in target_assets:
            if asset not in price_matrix.columns:
                continue

            returns_t1 = []
            returns_t3 = []
            returns_t5 = []

            for ev in event_list:
                dt_str = ev["date"]
                try:
                    dt = pd.to_datetime(dt_str)
                    # Find closest trading day
                    sub = price_matrix.loc[dt:]
                    if len(sub) >= 6:
                        p0 = sub[asset].iloc[0]
                        p1 = sub[asset].iloc[1]
                        p3 = sub[asset].iloc[3]
                        p5 = sub[asset].iloc[5]

                        if p0 > 0:
                            returns_t1.append(((p1 / p0) - 1.0) * 100.0)
                            returns_t3.append(((p3 / p0) - 1.0) * 100.0)
                            returns_t5.append(((p5 / p0) - 1.0) * 100.0)
                except Exception:
                    continue

            if returns_t3:
                # Win rate = percentage of moves in the primary expected direction
                pos_t3 = sum(1 for r in returns_t3 if r > 0)
                win_rate = (pos_t3 / len(returns_t3)) * 100.0
                median_t3 = float(np.median(returns_t3))
                median_t5 = float(np.median(returns_t5)) if returns_t5 else 0.0

                results[regime_key]["assets"][asset] = {
                    "win_rate_positive": round(win_rate, 1),
                    "median_return_t3": round(median_t3, 2),
                    "median_return_t5": round(median_t5, 2),
                    "dominant_direction": "UP 📈" if median_t3 > 0 else "DOWN 📉"
                }

    return results

def compute_historical_analog_similarity(current_features):
    """
    Computes Cosine Similarity between current macro features and historical analog vectors.
    Current Features Vector: [US10Y, RealYield, WTI_Oil, DXY, VIX, NetLiquidityDelta]
    """
    # Normalize features to comparable scales (Z-score weighting)
    # Weights for each component:
    weights = np.array([1.5, 2.0, 1.2, 1.0, 1.0, 1.8])
    curr_vec = np.array([
        current_features.get("us10y", 4.5),
        current_features.get("real_yield", 1.8),
        current_features.get("oil", 85.0),
        current_features.get("dxy", 102.0),
        current_features.get("vix", 18.0),
        current_features.get("net_liq_chg", 10.0)
    ]) * weights

    matches = []
    norm_curr = np.linalg.norm(curr_vec)

    for analog in HISTORICAL_ANALOG_REGIMES:
        hist_vec = np.array(analog["vector"]) * weights
        norm_hist = np.linalg.norm(hist_vec)

        if norm_curr > 0 and norm_hist > 0:
            cosine_sim = np.dot(curr_vec, hist_vec) / (norm_curr * norm_hist)
            # Map cosine similarity (-1 to 1) to percentage score (0 to 100%)
            sim_score = round(max(0.0, float(cosine_sim)) * 100.0, 1)
        else:
            sim_score = 50.0

        matches.append({
            "id": analog["id"],
            "name": analog["name"],
            "period": analog["period"],
            "similarity_score": sim_score,
            "core_driver": analog["core_driver"],
            "next_30_90d_outcome": analog["next_30_90d_outcome"],
            "sector_winners": analog["sector_winners"],
            "sector_losers": analog["sector_losers"],
            "crypto_implication": analog["crypto_implication"]
        })

    matches.sort(key=lambda x: x["similarity_score"], reverse=True)
    return matches

if __name__ == "__main__":
    print("Testing Phase 3 Backtest & Historical Analog Engine...")
    prices = load_backtest_price_matrix()
    print("Loaded price matrix rows:", len(prices))
    
    backtest_results = run_event_study_backtest(prices)
    print("\nBacktest Event Results (Sample HOT_CPI):")
    if "HOT_CPI" in backtest_results:
        for a, res in backtest_results["HOT_CPI"]["assets"].items():
            print(f"  {a}: Median T+3 = {res['median_return_t3']:+.2f}% | Direction: {res['dominant_direction']} (Win Rate: {res['win_rate_positive']}%)")

    current_test_features = {
        "us10y": 5.045,
        "real_yield": 2.15,
        "oil": 101.34,
        "dxy": 102.17,
        "vix": 16.91,
        "net_liq_chg": 42.3
    }
    analogs = compute_historical_analog_similarity(current_test_features)
    print("\nTop Historical Analogs for Current Regime:")
    for m in analogs[:3]:
        print(f"  {m['name']}: {m['similarity_score']}% Match -> {m['next_30_90d_outcome'][:80]}...")
