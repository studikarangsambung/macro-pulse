import os
import requests
import pandas as pd
import numpy as np
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

print("1. Fetching Macro Features from FRED & Yahoo Finance...")
cpi = get_fred_series("CPIAUCSL", "1970-01-01")
indpro = get_fred_series("INDPRO", "1970-01-01")
gs10 = get_fred_series("GS10", "1970-01-01")  # 10Y Treasury Rate
fedfunds = get_fred_series("FEDFUNDS", "1970-01-01")  # Effective Fed Funds Rate
oil_fred = get_fred_series("WTISPLC", "1970-01-01")  # WTI Crude Oil Price

sp500 = yf.download("^GSPC", start="1970-01-01", progress=False)["Close"]
if isinstance(sp500, pd.DataFrame):
    sp500 = sp500.iloc[:, 0]
sp500_monthly = sp500.resample("ME").last()

# Merge monthly
df = pd.DataFrame({
    "sp500": sp500_monthly,
    "cpi": cpi.resample("ME").last(),
    "indpro": indpro.resample("ME").last(),
    "gs10": gs10.resample("ME").last(),
    "fedfunds": fedfunds.resample("ME").last(),
    "oil": oil_fred.resample("ME").last()
}).dropna()

# 2. Feature Engineering for ML
# Growth features
df["growth_yoy"] = df["indpro"].pct_change(12) * 100
df["growth_mom"] = df["indpro"].pct_change(3) * 100
df["growth_accel"] = df["growth_yoy"] - df["growth_yoy"].shift(6)

# Inflation features
df["cpi_yoy"] = df["cpi"].pct_change(12) * 100
df["cpi_accel"] = df["cpi_yoy"] - df["cpi_yoy"].shift(6)

# Monetary & Rates features
df["yield_curve_slope"] = df["gs10"] - df["fedfunds"]  # 10Y - Fed Funds (Curve Inversion / Steepening)
df["rate_1y_chg"] = df["gs10"] - df["gs10"].shift(12)

# Commodity / Energy Shock feature
df["oil_yoy"] = df["oil"].pct_change(12) * 100
df["oil_trend"] = df["oil"] / df["oil"].rolling(12).mean() - 1.0

# S&P 500 Market Momentum & Volatility proxy
df["sp500_mom12"] = df["sp500"].pct_change(12) * 100
df["sp500_vol6"] = df["sp500"].pct_change().rolling(6).std() * np.sqrt(12) * 100

# Ground Truth Labels (Historical 4-Quadrants)
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

X = df[feature_cols]
y = df["regime_label"]

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, index=X.index, columns=feature_cols)

print(f"Dataset shape: {X.shape}, covering {X.index[0].strftime('%Y-%m')} to {X.index[-1].strftime('%Y-%m')}")

# 3. Supervised ML: Random Forest Classifier
rf = RandomForestClassifier(n_estimators=300, max_depth=6, random_state=42, min_samples_split=5)
# Train on historical data up to last 12 months, or full dataset to evaluate current point
rf.fit(X_scaled, y)

# Predict Current State
current_features = X_scaled[-1:]
current_date = X.index[-1]
predicted_regime = rf.predict(current_features)[0]
predicted_probs = rf.predict_proba(current_features)[0]
prob_dict = dict(zip(rf.classes_, predicted_probs))

print("\n" + "="*50)
print(f"[ML] MACHINE LEARNING REGIME DETECTION (Date: {current_date.strftime('%B %Y')})")
print("="*50)
print(f"PREDIKSI REZIM SAAT INI: >>> {predicted_regime} <<<")
print("\nDISTRIBUSI PROBABILITAS SOFTMAX (RANDOM FOREST):")
for regime_name, prob in sorted(prob_dict.items(), key=lambda x: x[1], reverse=True):
    bar = "=" * int(prob * 30)
    print(f"- {regime_name:<30}: {prob*100:5.1f}% | {bar}")

# Feature Importances
importances = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=False)
print("\nTOP FEATURE IMPORTANCES (PENGGERAK KEPUTUSAN ML):")
for feat, imp in importances.items():
    print(f"- {feat:<20}: {imp*100:4.1f}%")

# 4. Unsupervised ML: Gaussian Mixture Model (GMM Clustering)
gmm = GaussianMixture(n_components=4, covariance_type='full', random_state=42)
gmm_clusters = gmm.fit_predict(X_scaled)
gmm_probs = gmm.predict_proba(current_features)[0]
current_cluster = gmm.predict(current_features)[0]

print(f"\nUNSUPERVISED GMM CLUSTER SAAT INI: Cluster {current_cluster} (Keyakinan: {gmm_probs[current_cluster]*100:.1f}%)")

# 5. Dimensionality Reduction (PCA 2D Projection)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

pca_df = pd.DataFrame(X_pca, index=X.index, columns=["PC1_Financial_Conditions", "PC2_Cost_Shock"])
pca_df["regime"] = y

print(f"\nPCA Explained Variance: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, PC2={pca.explained_variance_ratio_[1]*100:.1f}%")
current_pca = pca_df.iloc[-1]
print(f"Posisi Titik Hari Ini di Ruang PCA: PC1={current_pca['PC1_Financial_Conditions']:.2f}, PC2={current_pca['PC2_Cost_Shock']:.2f}")

# Save results for plotting
pca_df.to_csv("d:/SAHAM/chart/macro_ml_pca.csv")
