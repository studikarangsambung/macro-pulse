import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, adjusted_rand_score
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

print("1. Loading Macro & Market Data...")
cpi = get_fred_series("CPIAUCSL", "1970-01-01")
indpro = get_fred_series("INDPRO", "1970-01-01")
gs10 = get_fred_series("GS10", "1970-01-01")
fedfunds = get_fred_series("FEDFUNDS", "1970-01-01")
oil = get_fred_series("WTISPLC", "1970-01-01")

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
    "oil": oil.resample("ME").last()
}).dropna()

# Feature engineering
df["growth_yoy"] = df["indpro"].pct_change(12) * 100
df["growth_accel"] = df["growth_yoy"] - df["growth_yoy"].shift(6)

df["cpi_yoy"] = df["cpi"].pct_change(12) * 100
df["cpi_accel"] = df["cpi_yoy"] - df["cpi_yoy"].shift(6)

df["yield_curve_slope"] = df["gs10"] - df["fedfunds"]
df["rate_1y_chg"] = df["gs10"] - df["gs10"].shift(12)

df["oil_yoy"] = df["oil"].pct_change(12) * 100
df["oil_trend"] = df["oil"] / df["oil"].rolling(12).mean() - 1.0

df["sp500_mom12"] = df["sp500"].pct_change(12) * 100
df["sp500_vol6"] = df["sp500"].pct_change().rolling(6).std() * np.sqrt(12) * 100
df["sp500_ret"] = df["sp500"].pct_change()

# Ground Truth Labels
def assign_quadrant(row):
    g_up = row["growth_accel"] > 0
    i_up = row["cpi_accel"] > 0
    if g_up and i_up:
        return "Q1_Reflasi"
    elif g_up and not i_up:
        return "Q2_Disinflasi_Boom"
    elif not g_up and i_up:
        return "Q3_Stagflasi"
    else:
        return "Q4_Deflasi_Kontraksi"

df["ground_truth"] = df.apply(assign_quadrant, axis=1)
df = df.dropna()

feature_cols = [
    "growth_yoy", "growth_accel",
    "cpi_yoy", "cpi_accel",
    "yield_curve_slope", "rate_1y_chg",
    "oil_yoy", "oil_trend",
    "sp500_mom12", "sp500_vol6"
]

print(f"Data ready: {len(df)} monthly observations ({df.index[0].strftime('%Y-%m')} to {df.index[-1].strftime('%Y-%m')})")

# 2. Walk-Forward Out-Of-Sample (OOS) Testing
# Minimum warm-up training window: 120 months (10 years)
min_train = 120

oos_preds_rf = []
oos_preds_lr = []
oos_preds_heur = []
oos_actual = []
oos_dates = []

# Heuristic Rule:
# If oil_trend > 0.15 and rate_1y_chg > 0.5 -> Q3_Stagflasi
# Else if growth_yoy > 2.5 and cpi_yoy < 3.0 -> Q2_Disinflasi_Boom
# Else if growth_yoy > 2.0 and cpi_yoy >= 3.0 -> Q1_Reflasi
# Else -> Q4_Deflasi_Kontraksi
def predict_heuristic(row):
    if row["oil_trend"] > 0.10 and row["yield_curve_slope"] < 0.2:
        return "Q3_Stagflasi"
    elif row["growth_yoy"] > 2.0 and row["cpi_accel"] <= 0:
        return "Q2_Disinflasi_Boom"
    elif row["growth_yoy"] > 1.5 and row["cpi_accel"] > 0:
        return "Q1_Reflasi"
    else:
        return "Q4_Deflasi_Kontraksi"

print("2. Running Walk-Forward Out-Of-Sample Validation...")
for t in range(min_train, len(df)):
    train_data = df.iloc[:t]
    test_row = df.iloc[t:t+1]
    
    X_tr = train_data[feature_cols]
    y_tr = train_data["ground_truth"]
    X_te = test_row[feature_cols]
    y_te = test_row["ground_truth"].values[0]
    
    scaler = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_tr)
    X_te_sc = scaler.transform(X_te)
    
    # 1. Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X_tr_sc, y_tr)
    pred_rf = rf.predict(X_te_sc)[0]
    
    # 2. Logistic Regression (Linear Benchmark)
    lr = LogisticRegression(max_iter=500, random_state=42)
    lr.fit(X_tr_sc, y_tr)
    pred_lr = lr.predict(X_te_sc)[0]
    
    # 3. Rule-Based Heuristic
    pred_heur = predict_heuristic(test_row.iloc[0])
    
    oos_preds_rf.append(pred_rf)
    oos_preds_lr.append(pred_lr)
    oos_preds_heur.append(pred_heur)
    oos_actual.append(y_te)
    oos_dates.append(test_row.index[0])

# Unsupervised Clustering (GMM) - Fit on full scaled dataset
scaler = StandardScaler()
X_all_sc = scaler.fit_transform(df[feature_cols])
gmm = GaussianMixture(n_components=4, covariance_type='full', random_state=42)
gmm_clusters = gmm.fit_predict(X_all_sc)

# Map GMM clusters to closest ground truth label
gmm_df = pd.DataFrame({"cluster": gmm_clusters, "ground_truth": df["ground_truth"]})
cluster_map = {}
for c in range(4):
    sub = gmm_df[gmm_df["cluster"] == c]
    if len(sub) > 0:
        cluster_map[c] = sub["ground_truth"].mode()[0]
    else:
        cluster_map[c] = "Q4_Deflasi_Kontraksi"

gmm_mapped = [cluster_map[c] for c in gmm_clusters[min_train:]]

# Compute Classification Accuracy Metrics
methods = {
    "Supervised ML (Random Forest)": oos_preds_rf,
    "Linear Baseline (Logistic Regression)": oos_preds_lr,
    "Unsupervised ML (GMM Clustering)": gmm_mapped,
    "Rule-Based Heuristik (Thresholds)": oos_preds_heur
}

results = []
for name, preds in methods.items():
    acc = accuracy_score(oos_actual, preds) * 100
    prec = precision_score(oos_actual, preds, average='macro', zero_division=0) * 100
    rec = recall_score(oos_actual, preds, average='macro', zero_division=0) * 100
    f1 = f1_score(oos_actual, preds, average='macro', zero_division=0) * 100
    
    # Financial / Trading Strategy Simulation based on Regime:
    # Rule: If predicted Q2 (Boom) -> Long S&P 500 (100%)
    # If predicted Q1 (Reflasi) -> Long S&P 500 (70%) + Cash (30%)
    # If predicted Q3 (Stagflasi) -> Cash (100%) / Defensive (Risk-Off)
    # If predicted Q4 (Deflasi) -> Cash (50%) + S&P 500 (50%)
    oos_df = pd.DataFrame({
        "pred": preds,
        "sp_ret": df["sp500_ret"].iloc[min_train:].values
    }, index=oos_dates)
    
    strat_weights = []
    for p in oos_df["pred"]:
        if p == "Q2_Disinflasi_Boom":
            strat_weights.append(1.0)
        elif p == "Q1_Reflasi":
            strat_weights.append(0.7)
        elif p == "Q3_Stagflasi":
            strat_weights.append(0.0) # Avoid equity drawdown
        else:
            strat_weights.append(0.5)
            
    oos_df["strat_ret"] = oos_df["sp_ret"] * strat_weights
    
    # Strategy Metrics
    ann_ret = (1 + oos_df["strat_ret"].mean())**12 - 1
    vol = oos_df["strat_ret"].std() * np.sqrt(12)
    sharpe = (ann_ret - 0.03) / vol if vol > 0 else 0
    cum_ret = (1 + oos_df["strat_ret"]).cumprod()
    peak = cum_ret.cummax()
    mdd = ((cum_ret - peak) / peak).min() * 100
    
    results.append({
        "Metode": name,
        "Out-of-Sample Accuracy": f"{acc:.1f}%",
        "Macro Precision": f"{prec:.1f}%",
        "Macro Recall": f"{rec:.1f}%",
        "Macro F1-Score": f"{f1:.1f}%",
        "Strategy Ann. Return": f"{ann_ret*100:+.1f}%",
        "Strategy Sharpe": f"{sharpe:.2f}",
        "Max Drawdown (MDD)": f"{mdd:.1f}%"
    })

# Add Benchmark Buy & Hold S&P 500
bh_ret = df["sp500_ret"].iloc[min_train:]
bh_ann_ret = (1 + bh_ret.mean())**12 - 1
bh_vol = bh_ret.std() * np.sqrt(12)
bh_sharpe = (bh_ann_ret - 0.03) / bh_vol if bh_vol > 0 else 0
bh_cum = (1 + bh_ret).cumprod()
bh_mdd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min() * 100

results.append({
    "Metode": "Benchmark: Buy & Hold S&P 500",
    "Out-of-Sample Accuracy": "N/A",
    "Macro Precision": "N/A",
    "Macro Recall": "N/A",
    "Macro F1-Score": "N/A",
    "Strategy Ann. Return": f"{bh_ann_ret*100:+.1f}%",
    "Strategy Sharpe": f"{bh_sharpe:.2f}",
    "Max Drawdown (MDD)": f"{bh_mdd:.1f}%"
})

res_df = pd.DataFrame(results)
print("\n" + "="*80)
print("HASIL PENGUJIAN AKURASI METODE REGIME DETECTION (1981 - 2026 OOS)")
print("="*80)
print(res_df.to_string(index=False))

# Confusion Matrix for Random Forest
cm = confusion_matrix(oos_actual, oos_preds_rf, labels=["Q1_Reflasi", "Q2_Disinflasi_Boom", "Q3_Stagflasi", "Q4_Deflasi_Kontraksi"])
print("\nCONFUSION MATRIX RANDOM FOREST (OUT-OF-SAMPLE):")
print(pd.DataFrame(cm, 
                   index=["Aktual Q1", "Aktual Q2", "Aktual Q3", "Aktual Q4"], 
                   columns=["Pred Q1", "Pred Q2", "Pred Q3", "Pred Q4"]))

# Export CSV
res_df.to_csv("d:/SAHAM/chart/regime_accuracy_comparison.csv", index=False)
