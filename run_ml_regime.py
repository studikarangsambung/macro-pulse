import pandas as pd
import numpy as np
import requests
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

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

cpi = get_fred_series("CPIAUCSL", "1970-01-01")
indpro = get_fred_series("INDPRO", "1970-01-01")
gs10 = get_fred_series("GS10", "1970-01-01")
fedfunds = get_fred_series("FEDFUNDS", "1970-01-01")
oil_fred = get_fred_series("WTISPLC", "1970-01-01")

sp500 = yf.download("^GSPC", start="1970-01-01", progress=False)["Close"]
if isinstance(sp500, pd.DataFrame):
    sp500 = sp500.iloc[:, 0]
sp500_monthly = sp500.resample("ME").last()

df = pd.DataFrame({
    "sp500": sp500_monthly,
    "cpi": cpi.resample("ME").last(),
    "indpro": indpro.resample("ME").last(),
    "gs10": gs10.resample("ME").last(),
    "fedfunds": fedfunds.resample("ME").last(),
    "oil": oil_fred.resample("ME").last()
}).dropna()

# Add October 2026 Live Row
# Live data: WTI Oil = 102.58, 10Y Yield = 4.989, Fed Funds = 4.83, SP500 = 5815
last_date = pd.to_datetime("2026-10-30")
oct_row = {
    "sp500": 5815.0,
    "cpi": df["cpi"].iloc[-1] * (1 + 0.0035),  # est +0.35% MoM due to oil shock
    "indpro": df["indpro"].iloc[-1] * (1 - 0.002), # est -0.2% MoM deceleration
    "gs10": 4.989,
    "fedfunds": 4.83,
    "oil": 102.58
}
df.loc[last_date] = oct_row

# Feature engineering
df["growth_yoy"] = df["indpro"].pct_change(12) * 100
df["growth_mom"] = df["indpro"].pct_change(3) * 100
df["growth_accel"] = df["growth_yoy"] - df["growth_yoy"].shift(6)

df["cpi_yoy"] = df["cpi"].pct_change(12) * 100
df["cpi_accel"] = df["cpi_yoy"] - df["cpi_yoy"].shift(6)

df["yield_curve_slope"] = df["gs10"] - df["fedfunds"]
df["rate_1y_chg"] = df["gs10"] - df["gs10"].shift(12)

df["oil_yoy"] = df["oil"].pct_change(12) * 100
df["oil_trend"] = df["oil"] / df["oil"].rolling(12).mean() - 1.0

df["sp500_mom12"] = df["sp500"].pct_change(12) * 100
df["sp500_vol6"] = df["sp500"].pct_change().rolling(6).std() * np.sqrt(12) * 100

def assign_quadrant(row):
    g_up = row["growth_accel"] > 0
    i_up = row["cpi_accel"] > 0
    if g_up and i_up:
        return "Kuadran I: Reflasi"
    elif g_up and not i_up:
        return "Kuadran II: Disinflasi Boom"
    elif not g_up and i_up:
        return "Kuadran III: Stagflasi"
    else:
        return "Kuadran IV: Deflasi Kontraksi"

df["regime_label"] = df.apply(assign_quadrant, axis=1)
df = df.dropna()

feature_cols = [
    "growth_yoy", "growth_accel",
    "cpi_yoy", "cpi_accel",
    "yield_curve_slope", "rate_1y_chg",
    "oil_yoy", "oil_trend",
    "sp500_mom12", "sp500_vol6"
]

X_train = df.iloc[:-1][feature_cols]
y_train = df.iloc[:-1]["regime_label"]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(df.iloc[-1:][feature_cols])

# Train Random Forest Classifier
rf = RandomForestClassifier(n_estimators=300, max_depth=6, random_state=42)
rf.fit(X_train_scaled, y_train)

pred_today = rf.predict(X_test_scaled)[0]
probs_today = rf.predict_proba(X_test_scaled)[0]
prob_dict = dict(zip(rf.classes_, probs_today))

print("="*60)
print("PREDIKSI MACHINE LEARNING TERKINI (30 OKTOBER 2026)")
print("="*60)
print(f"Hasil Klasifikasi Model ML: >>> {pred_today} <<<")
print("\nDistribusi Probabilitas Model:")
for k, v in sorted(prob_dict.items(), key=lambda x: x[1], reverse=True):
    bar = "=" * int(v * 30)
    print(f"- {k:<30}: {v*100:5.1f}% | {bar}")

# GMM Clustering
gmm = GaussianMixture(n_components=4, covariance_type='full', random_state=42)
gmm.fit(X_train_scaled)
gmm_cluster = gmm.predict(X_test_scaled)[0]
gmm_prob = gmm.predict_proba(X_test_scaled)[0]
print(f"\nUnsupervised GMM Cluster: Cluster {gmm_cluster} (Probabilitas: {gmm_prob[gmm_cluster]*100:.1f}%)")

# PCA Projection
pca = PCA(n_components=2)
X_all_scaled = scaler.fit_transform(df[feature_cols])
X_pca = pca.fit_transform(X_all_scaled)

pca_today = X_pca[-1]
print(f"Koordinat PCA Terkini: PC1={pca_today[0]:.2f}, PC2={pca_today[1]:.2f}")

# Generate ML Visualizer Plot
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=150)
fig.patch.set_facecolor('#0d130e')
ax1.set_facecolor('#131c14')
ax2.set_facecolor('#131c14')

# Subplot 1: Probability Distribution Bar Chart
labels = list(prob_dict.keys())
values = [prob_dict[k] * 100 for k in labels]
bar_colors = ["#d97706", "#10b981", "#ef4444", "#6366f1"]
colors_map = {
    "Kuadran I: Reflasi": "#d97706",
    "Kuadran II: Disinflasi Boom": "#10b981",
    "Kuadran III: Stagflasi": "#ef4444",
    "Kuadran IV: Deflasi Kontraksi": "#6366f1"
}
colors_ordered = [colors_map.get(k, "#ffffff") for k in labels]

bars = ax1.barh(labels, values, color=colors_ordered, edgecolor='#ffffff', linewidth=0.6, alpha=0.9)
ax1.set_xlim(0, 100)
ax1.set_xlabel("Probabilitas Softmax (%)", fontsize=11, fontweight='bold', color='#a3b899')
ax1.set_title("Machine Learning (Random Forest) Probability Distribution\nPosisi Rezim Makro per 30 Oktober 2026", fontsize=12, fontweight='bold', color='#e5ede3')
ax1.grid(True, axis='x', color='#263828', linestyle='--', linewidth=0.5)

for bar in bars:
    w = bar.get_width()
    ax1.annotate(f"{w:.1f}%", xy=(w, bar.get_y() + bar.get_height()/2),
                 xytext=(8, 0), textcoords="offset points", ha='left', va='center',
                 fontsize=10, fontweight='bold', color='#ffffff')

# Subplot 2: 2D PCA Space Scatter Plot
scatter_colors = [colors_map.get(r, "#888888") for r in df["regime_label"][:-1]]
ax2.scatter(X_pca[:-1, 0], X_pca[:-1, 1], c=scatter_colors, alpha=0.25, s=28, edgecolors='none', label='Data Historis (1971-2026)')

# Highlight Today's Position
ax2.scatter(pca_today[0], pca_today[1], c='#facc15', s=240, edgecolors='#ffffff', linewidth=2.5, zorder=5, label='POSISI SAAT INI (30 OKT 2026)')
ax2.annotate(f"POSISI KITA HARI INI\n({pred_today.split(':')[1].strip()})\n[PC1: {pca_today[0]:.2f}, PC2: {pca_today[1]:.2f}]",
             xy=(pca_today[0], pca_today[1]), xytext=(25, 25), textcoords="offset points",
             fontsize=9, fontweight='bold', color='#facc15',
             bbox=dict(boxstyle="round,pad=0.4", fc="#0d130e", ec="#facc15", lw=1.5, alpha=0.95),
             arrowprops=dict(arrowstyle="->", color="#facc15", lw=1.5))

ax2.set_xlabel(f"PC1: Kondisi Finansial & Momentum Pertumbuhan ({pca.explained_variance_ratio_[0]*100:.1f}% Var)", fontsize=10, fontweight='bold', color='#a3b899')
ax2.set_ylabel(f"PC2: Tekanan Inflasi & Shock Energi ({pca.explained_variance_ratio_[1]*100:.1f}% Var)", fontsize=10, fontweight='bold', color='#a3b899')
ax2.set_title("Proyeksi 2D PCA Makro (Principal Component Analysis)\nPosisi Ruang Multidimensi Pasar Modal", fontsize=12, fontweight='bold', color='#e5ede3')
ax2.grid(True, color='#263828', linestyle='--', linewidth=0.5)
ax2.legend(loc="upper left", facecolor="#131c14", edgecolor="#344e37", fontsize=8.5)

plt.tight_layout()
out_ml_png = "d:/SAHAM/chart/ml_regime_detection_chart.png"
plt.savefig(out_ml_png, facecolor=fig.get_facecolor(), edgecolor='none', dpi=180)
print(f"ML Chart saved: {out_ml_png}")
