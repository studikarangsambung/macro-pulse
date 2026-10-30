import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import yfinance as yf

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

df["growth_trend"] = df["indpro_yoy"].rolling(6).mean()
df["growth_dir"] = df["growth_trend"] - df["growth_trend"].shift(6)

df["cpi_trend"] = df["cpi_yoy"].rolling(6).mean()
df["cpi_dir"] = df["cpi_trend"] - df["cpi_trend"].shift(6)

df["sp500_ret"] = df["sp500"].pct_change()
df = df.dropna()

def assign_quadrant_info(row):
    g_up = row["growth_dir"] > 0
    i_up = row["cpi_dir"] > 0
    if g_up and i_up:
        return "Kuadran I: Reflasi", "Growth ↑ · Inflasi ↑", "#d97706"
    elif g_up and not i_up:
        return "Kuadran II: Disinflasi Boom", "Growth ↑ · Inflasi ↓", "#10b981"
    elif not g_up and i_up:
        return "Kuadran III: Stagflasi", "Growth ↓ · Inflasi ↑", "#ef4444"
    else:
        return "Kuadran IV: Deflasi Kontraksi", "Growth ↓ · Inflasi ↓", "#6366f1"

res = df.apply(assign_quadrant_info, axis=1)
df["quadrant"] = [r[0] for r in res]
df["quad_desc"] = [r[1] for r in res]
df["color"] = [r[2] for r in res]

# Create Interactive Plotly Figure
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                    row_heights=[0.75, 0.25],
                    subplot_titles=("S&P 500 Index (Log Scale) & 4-Kuadran Makro Regime Shading", 
                                    "Indikator Penggerak: Pertumbuhan Riil (INDPRO YoY) vs Inflasi (CPI YoY)"))

# Main S&P 500 trace
fig.add_trace(go.Scatter(
    x=df.index, y=df["sp500"],
    mode='lines',
    line=dict(color='#ffffff', width=2),
    name='S&P 500 Index',
    customdata=np.stack((df["quadrant"], df["quad_desc"], df["growth_trend"], df["cpi_trend"]), axis=-1),
    hovertemplate="<b>%{x|%b %Y}</b><br>S&P 500: <b>$%{y:,.2f}</b><br>Rezim: <b>%{customdata[0]}</b> (%{customdata[1]})<br>Growth Trend: %{customdata[2]:.2f}% | CPI Trend: %{customdata[3]:.2f}%<extra></extra>"
), row=1, col=1)

# Add Shaded Background Bands per continuous regime
df["regime_shift"] = (df["quadrant"] != df["quadrant"].shift()).astype(int)
df["regime_group"] = df["regime_shift"].cumsum()

shapes = []
for group_id, group_data in df.groupby("regime_group"):
    q = group_data["quadrant"].iloc[0]
    color = group_data["color"].iloc[0]
    x0 = group_data.index[0]
    x1 = group_data.index[-1]
    fig.add_vrect(
        x0=x0, x1=x1,
        fillcolor=color, opacity=0.18,
        layer="below", line_width=0,
        row=1, col=1
    )

# Lower subplot: Growth & Inflation trends
fig.add_trace(go.Scatter(
    x=df.index, y=df["growth_trend"],
    mode='lines',
    line=dict(color='#38bdf8', width=1.5),
    name='Growth Trend (INDPRO YoY 6M)'
), row=2, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df["cpi_trend"],
    mode='lines',
    line=dict(color='#f43f5e', width=1.5),
    name='Inflation Trend (CPI YoY 6M)'
), row=2, col=1)

fig.update_yaxes(type="log", title_text="S&P 500 (Log Scale)", row=1, col=1, gridcolor='#263828')
fig.update_yaxes(title_text="YoY Trend (%)", row=2, col=1, gridcolor='#263828')
fig.update_xaxes(gridcolor='#263828')

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d130e",
    plot_bgcolor="#131c14",
    title="<b>PENGUJIAN HISTORIS SIKLUS MAKRO (1971 - 2026): S&P 500 vs 4-KUADRAN</b><br><sup>Durasi rata-rata: Reflasi 7.8 bln | Disinflasi Boom 6.3 bln | Stagflasi 6.6 bln | Deflasi 6.4 bln</sup>",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=60, r=40, t=90, b=50),
    height=750
)

out_html = "d:/SAHAM/chart/macro_quadrants_interactive.html"
fig.write_html(out_html, include_plotlyjs='cdn')
print("Interactive HTML chart saved:", out_html)
