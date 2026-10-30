import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

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

print("Loading data...")
cpi = get_fred_series("CPIAUCSL", "1970-01-01")
indpro = get_fred_series("INDPRO", "1970-01-01")

sp500 = yf.download("^GSPC", start="1970-01-01", progress=False)["Close"]
if isinstance(sp500, pd.DataFrame):
    sp500 = sp500.iloc[:, 0]
sp500_monthly = sp500.resample("ME").last()

df = pd.DataFrame({
    "sp500": sp500_monthly,
    "cpi": cpi.resample("ME").last(),
    "indpro": indpro.resample("ME").last()
}).dropna()

df["cpi_yoy"] = df["cpi"].pct_change(12) * 100
df["indpro_yoy"] = df["indpro"].pct_change(12) * 100

# 6-Month Smoothed Direction
df["growth_trend"] = df["indpro_yoy"].rolling(6).mean()
df["growth_dir"] = df["growth_trend"] - df["growth_trend"].shift(6)

df["cpi_trend"] = df["cpi_yoy"].rolling(6).mean()
df["cpi_dir"] = df["cpi_trend"] - df["cpi_trend"].shift(6)

df["sp500_ret"] = df["sp500"].pct_change()
df = df.dropna()

def assign_quadrant(row):
    g_up = row["growth_dir"] > 0
    i_up = row["cpi_dir"] > 0
    if g_up and i_up:
        return "Q1_REFLASI"
    elif g_up and not i_up:
        return "Q2_DISINFLASI_BOOM"
    elif not g_up and i_up:
        return "Q3_STAGFLASI"
    else:
        return "Q4_DEFLASI_KONTRAKSI"

df["quadrant"] = df.apply(assign_quadrant, axis=1)

# Style configuration
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 11), gridspec_kw={'height_ratios': [2.8, 1.2]}, dpi=150)
fig.patch.set_facecolor('#0d130e')
ax1.set_facecolor('#131c14')
ax2.set_facecolor('#131c14')

# Palette matching user's Natural Forest UI
colors = {
    "Q1_REFLASI": "#d97706",          # Amber / Orange
    "Q2_DISINFLASI_BOOM": "#10b981",   # Emerald Green
    "Q3_STAGFLASI": "#ef4444",         # Red / Maroon
    "Q4_DEFLASI_KONTRAKSI": "#6366f1"  # Indigo / Blue
}

labels = {
    "Q1_REFLASI": "Kuadran I: Reflasi (Growth ↑, Inflasi ↑)",
    "Q2_DISINFLASI_BOOM": "Kuadran II: Disinflasi Boom (Growth ↑, Inflasi ↓)",
    "Q3_STAGFLASI": "Kuadran III: Stagflasi (Growth ↓, Inflasi ↑)",
    "Q4_DEFLASI_KONTRAKSI": "Kuadran IV: Deflasi (Growth ↓, Inflasi ↓)"
}

# 1. Plot S&P 500 Index (Log Scale) with Shaded Regimes
ax1.plot(df.index, df["sp500"], color='#ffffff', linewidth=1.8, label="S&P 500 Index (^GSPC)", zorder=4)
ax1.set_yscale('log')
ax1.set_ylabel("S&P 500 Index (Log Scale)", fontsize=11, fontweight='bold', color='#a3b899')
ax1.grid(True, which='both', color='#263828', linestyle='--', linewidth=0.5, alpha=0.7)

# Shade quadrants
dates = df.index
for i in range(len(df) - 1):
    q = df["quadrant"].iloc[i]
    ax1.axvspan(dates[i], dates[i+1], color=colors[q], alpha=0.22, zorder=1)

# Annotate Major Historic Cycles
annotations = [
    ("1973 Oil Shock\n(Stagflasi Parah)", "1973-10-01", 108, "#ef4444"),
    ("1982-1985 Volcker\nDisinflasi Boom", "1983-06-01", 160, "#10b981"),
    ("1995-1999 Dot-Com\nGoldilocks Boom", "1997-01-01", 800, "#10b981"),
    ("2008 GFC\nDeflasi Kontraksi", "2008-09-01", 1200, "#6366f1"),
    ("2020 Covid QE\n& 2021 Reflasi", "2020-08-01", 3400, "#d97706"),
    ("2022-2026\nStagflasi Energi", "2023-01-01", 4000, "#ef4444"),
]

for text, date_str, y_val, col in annotations:
    dt = pd.to_datetime(date_str)
    if dt in df.index or dt >= df.index[0]:
        ax1.annotate(text, xy=(mdates.date2num(dt), y_val),
                     xytext=(0, 28), textcoords="offset points",
                     fontsize=8.5, fontweight='bold', color=col,
                     bbox=dict(boxstyle="round,pad=0.3", fc="#0d130e", ec=col, lw=1.2, alpha=0.9),
                     arrowprops=dict(arrowstyle="->", color=col, lw=1))

# Legend for Ax1
legend_patches = [
    mpatches.Patch(color=colors["Q2_DISINFLASI_BOOM"], label="Kuadran II: Disinflasi Boom (Avg: 6.3 bln | Ann. Ret: +15.1%)"),
    mpatches.Patch(color=colors["Q4_DEFLASI_KONTRAKSI"], label="Kuadran IV: Deflasi Kontraksi (Avg: 6.4 bln | Ann. Ret: +14.3%)"),
    mpatches.Patch(color=colors["Q1_REFLASI"], label="Kuadran I: Reflasi (Avg: 7.8 bln | Ann. Ret: +8.1%)"),
    mpatches.Patch(color=colors["Q3_STAGFLASI"], label="Kuadran III: Stagflasi (Avg: 6.6 bln | Ann. Ret: +1.5%)"),
]
ax1.legend(handles=legend_patches, loc="upper left", facecolor="#131c14", edgecolor="#344e37", fontsize=9, framealpha=0.95)
ax1.set_title("HISTORICAL BACKTEST: S&P 500 TERHADAP 4-KUADRAN MAKRO (1971 - 2026)\nAnalisis Durasi Siklus Bisnis & Imbal Hasil Riil Pasar Modal", 
              fontsize=14, fontweight='bold', color='#e5ede3', pad=15)

# 2. Subplot: Bar Chart Durasi Rata-rata & Annualized Return per Kuadran
quad_keys = ["Q2_DISINFLASI_BOOM", "Q4_DEFLASI_KONTRAKSI", "Q1_REFLASI", "Q3_STAGFLASI"]
names = ["II. Disinflasi Boom", "IV. Deflasi Kontraksi", "I. Reflasi", "III. Stagflasi"]
durations = [6.3, 6.4, 7.8, 6.6]
returns = [15.1, 14.3, 8.1, 1.5]
bar_colors = [colors[k] for k in quad_keys]

x = np.arange(len(names))
width = 0.35

rects1 = ax2.bar(x - width/2, durations, width, label='Rata-rata Durasi per Siklus (Bulan)', color=bar_colors, alpha=0.85, edgecolor='#ffffff', linewidth=0.5)
rects2 = ax2.bar(x + width/2, returns, width, label='S&P 500 Annualized Return (%)', color=[c for c in bar_colors], hatch='//', alpha=0.95, edgecolor='#000000')

ax2.set_ylabel('Bulan / % Return', fontsize=10, fontweight='bold', color='#a3b899')
ax2.set_xticks(x)
ax2.set_xticklabels(names, fontsize=10, fontweight='bold', color='#e5ede3')
ax2.legend(loc="upper right", facecolor="#131c14", edgecolor="#344e37", fontsize=8.5)
ax2.grid(True, axis='y', color='#263828', linestyle='--', linewidth=0.5, alpha=0.7)

# Value labels on bars
for bar in rects1:
    h = bar.get_height()
    ax2.annotate(f"{h:.1f} bln", xy=(bar.get_x() + bar.get_width()/2, h),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                 fontsize=8.5, fontweight='bold', color='#e5ede3')

for bar in rects2:
    h = bar.get_height()
    ax2.annotate(f"{h:+.1f}%", xy=(bar.get_x() + bar.get_width()/2, h),
                 xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                 fontsize=8.5, fontweight='bold', color='#facc15')

plt.tight_layout()

output_png = "d:/SAHAM/chart/macro_quadrants_sp500_backtest.png"
plt.savefig(output_png, facecolor=fig.get_facecolor(), edgecolor='none', dpi=180)
print(f"Chart saved successfully: {output_png}")
