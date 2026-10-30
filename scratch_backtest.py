import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

FRED_API_KEY = "99c703d28398c06080d7437d00040ae4"

def get_fred_series(series_id, start_date="1970-01-01"):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&observation_start={start_date}"
    r = requests.get(url, timeout=15)
    data = r.json().get("observations", [])
    df = pd.DataFrame(data)[["date", "value"]]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna().set_index("date")
    return df["value"]

print("Fetching FRED macro data...")
# CPI: Consumer Price Index
cpi = get_fred_series("CPIAUCSL", "1970-01-01")
# INDPRO: Industrial Production (Monthly proxy for Real Economic Output / Growth)
indpro = get_fred_series("INDPRO", "1970-01-01")

print("Fetching S&P 500 (^GSPC) data from Yahoo Finance...")
sp500 = yf.download("^GSPC", start="1970-01-01", progress=False)["Close"]
if isinstance(sp500, pd.DataFrame):
    sp500 = sp500.iloc[:, 0]
sp500_monthly = sp500.resample("ME").last()

# Combine into monthly dataframe
df = pd.DataFrame({
    "sp500": sp500_monthly,
    "cpi": cpi.resample("ME").last(),
    "indpro": indpro.resample("ME").last()
}).dropna()

# Calculate Year-over-Year (YoY) rates of change
df["cpi_yoy"] = df["cpi"].pct_change(12) * 100
df["indpro_yoy"] = df["indpro"].pct_change(12) * 100

# Direction (Acceleration vs Deceleration): 3-month momentum of YoY or YoY change vs previous month
df["cpi_dir"] = df["cpi_yoy"] - df["cpi_yoy"].shift(3)
df["growth_dir"] = df["indpro_yoy"] - df["indpro_yoy"].shift(3)

# Monthly returns of S&P 500
df["sp500_ret"] = df["sp500"].pct_change()

df = df.dropna()

# Classify into 4 Quadrants
def assign_quadrant(row):
    g_up = row["growth_dir"] > 0
    i_up = row["cpi_dir"] > 0
    
    if g_up and i_up:
        return "Kuadran I: Reflasi"
    elif g_up and not i_up:
        return "Kuadran II: Disinflasi Boom"
    elif not g_up and i_up:
        return "Kuadran III: Stagflasi"
    else:
        return "Kuadran IV: Deflasi Kontraksi"

df["quadrant"] = df.apply(assign_quadrant, axis=1)

# Analyze streak / duration
df["regime_shift"] = (df["quadrant"] != df["quadrant"].shift()).astype(int)
df["regime_group"] = df["regime_shift"].cumsum()

streaks = []
for group_id, group_data in df.groupby("regime_group"):
    quad = group_data["quadrant"].iloc[0]
    duration_months = len(group_data)
    start_date = group_data.index[0]
    end_date = group_data.index[-1]
    sp_ret = (group_data["sp500"].iloc[-1] / group_data["sp500"].iloc[0] - 1) * 100
    streaks.append({
        "quadrant": quad,
        "duration_months": duration_months,
        "start_date": start_date,
        "end_date": end_date,
        "sp_ret": sp_ret
    })

streak_df = pd.DataFrame(streaks)

print("\n=== HASIL BACKTEST DURASI REZIM MAKRO (1971 - 2026) ===")
summary = []
for quad in ["Kuadran I: Reflasi", "Kuadran II: Disinflasi Boom", "Kuadran III: Stagflasi", "Kuadran IV: Deflasi Kontraksi"]:
    q_streaks = streak_df[streak_df["quadrant"] == quad]["duration_months"]
    q_ret = df[df["quadrant"] == quad]["sp500_ret"]
    
    total_months = q_streaks.sum()
    pct_time = (total_months / len(df)) * 100
    avg_dur = q_streaks.mean()
    median_dur = q_streaks.median()
    max_dur = q_streaks.max()
    min_dur = q_streaks.min()
    
    # S&P 500 performance
    ann_ret = (1 + q_ret.mean())**12 - 1
    win_rate = (q_ret > 0).mean() * 100
    vol = q_ret.std() * np.sqrt(12) * 100
    sharpe = (ann_ret - 0.03) / (vol / 100) if vol > 0 else 0
    
    summary.append({
        "Kuadran": quad,
        "Total Bulan": total_months,
        "Proporsi Waktu": f"{pct_time:.1f}%",
        "Rata-rata Durasi (Bulan)": f"{avg_dur:.1f} bln",
        "Median Durasi": f"{median_dur:.0f} bln",
        "Durasi Terpanjang": f"{max_dur:.0f} bln",
        "S&P 500 Ann. Return": f"{ann_ret*100:+.1f}%",
        "Win Rate (Bulan +)": f"{win_rate:.1f}%",
        "Volatilitas Tahunan": f"{vol:.1f}%"
    })

sum_df = pd.DataFrame(summary)
print(sum_df.to_string(index=False))

# Export clean CSV
sum_df.to_csv("d:/SAHAM/chart/macro_quadrant_backtest_summary.csv", index=False)
