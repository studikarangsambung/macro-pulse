"""
Data Ingestion Pipeline for Macro, US Sectors, and Crypto Assets
Integrates Yahoo Finance and St. Louis Fed (FRED) API.
"""

import os
import sqlite3
import datetime
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from config import FRED_API_KEY, FRED_SERIES, TICKERS_MACRO, TICKERS_SECTORS, TICKERS_CRYPTO, DB_PATH

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for market prices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_prices (
        date TEXT,
        ticker TEXT,
        close REAL,
        change_1d_pct REAL,
        change_5d_pct REAL,
        change_20d_pct REAL,
        PRIMARY KEY (date, ticker)
    )
    """)
    
    # Table for FRED observations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fred_observations (
        date TEXT,
        series_id TEXT,
        value REAL,
        PRIMARY KEY (date, series_id)
    )
    """)
    
    # Table for Net Liquidity
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS net_liquidity (
        date TEXT PRIMARY KEY,
        walcl REAL,
        tga REAL,
        rrp REAL,
        net_liquidity_bil REAL,
        change_4w_bil REAL
    )
    """)
    
    conn.commit()
    conn.close()

def fetch_fred_series(series_id, limit=90):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json&sort_order=desc&limit={limit}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            obs = data.get("observations", [])
            clean_records = []
            for item in obs:
                val = item.get("value")
                if val != "." and val is not None:
                    try:
                        clean_records.append({"date": item["date"], "series_id": series_id, "value": float(val)})
                    except ValueError:
                        continue
            return pd.DataFrame(clean_records)
    except Exception as e:
        print(f"Error fetching FRED series {series_id}: {e}")
    return pd.DataFrame()

def sync_fred_data():
    conn = sqlite3.connect(DB_PATH)
    for sid in FRED_SERIES.keys():
        df = fetch_fred_series(sid, limit=120)
        if not df.empty:
            df.to_sql("fred_observations", conn, if_exists="replace" if sid == "WALCL" else "append", index=False)
            # Remove duplicates by date & series_id
            cursor = conn.cursor()
            cursor.execute("""
            DELETE FROM fred_observations 
            WHERE rowid NOT IN (
                SELECT MIN(rowid) FROM fred_observations GROUP BY date, series_id
            )
            """)
            conn.commit()
    conn.close()

def compute_net_liquidity():
    """
    Fed Net Liquidity = WALCL (Total Assets) - WTREGEN (TGA) - (RRPONTSYD * 1000)
    WALCL and WTREGEN are in Millions $, RRP is in Billions $.
    Result in Billions $.
    """
    conn = sqlite3.connect(DB_PATH)
    walcl = pd.read_sql_query("SELECT date, value as walcl FROM fred_observations WHERE series_id='WALCL' ORDER BY date ASC", conn)
    tga = pd.read_sql_query("SELECT date, value as tga FROM fred_observations WHERE series_id='WTREGEN' ORDER BY date ASC", conn)
    rrp = pd.read_sql_query("SELECT date, value as rrp FROM fred_observations WHERE series_id='RRPONTSYD' ORDER BY date ASC", conn)
    conn.close()
    
    if walcl.empty or tga.empty:
        return None
    
    walcl['date'] = pd.to_datetime(walcl['date'])
    tga['date'] = pd.to_datetime(tga['date'])
    rrp['date'] = pd.to_datetime(rrp['date'])
    
    # Merge on date, forward fill for weekly balance sheet matching daily RRP
    m = pd.merge(walcl, tga, on="date", how="outer")
    m = pd.merge(m, rrp, on="date", how="outer").sort_values("date")
    m = m.ffill().dropna().tail(90)
    
    # Net Liquidity in Billions USD
    m['net_liquidity_bil'] = (m['walcl'] - m['tga'] - (m['rrp'] * 1000.0)) / 1000.0
    m['change_4w_bil'] = m['net_liquidity_bil'].diff(periods=20)
    
    conn = sqlite3.connect(DB_PATH)
    m_to_save = m[['date', 'walcl', 'tga', 'rrp', 'net_liquidity_bil', 'change_4w_bil']].copy()
    m_to_save['date'] = m_to_save['date'].dt.strftime('%Y-%m-%d')
    m_to_save.to_sql("net_liquidity", conn, if_exists="replace", index=False)
    conn.close()
    return m.tail(1).to_dict(orient="records")[0] if not m.empty else None

def sync_market_data(days=90):
    all_tickers = list(TICKERS_MACRO.keys()) + list(TICKERS_SECTORS.keys()) + list(TICKERS_CRYPTO.keys())
    
    data = yf.download(all_tickers, period=f"{days}d", interval="1d", progress=False)
    if 'Close' not in data:
        print("Failed to download price data.")
        return
    
    closes = data['Close']
    records = []
    
    for ticker in all_tickers:
        if ticker in closes.columns:
            s = closes[ticker].dropna()
            if len(s) >= 2:
                for idx in range(max(0, len(s) - 30), len(s)):
                    dt = s.index[idx].strftime('%Y-%m-%d')
                    val = float(s.iloc[idx])
                    
                    chg_1d = float(((s.iloc[idx] / s.iloc[idx-1]) - 1.0) * 100.0) if idx > 0 else 0.0
                    chg_5d = float(((s.iloc[idx] / s.iloc[idx-5]) - 1.0) * 100.0) if idx >= 5 else chg_1d
                    chg_20d = float(((s.iloc[idx] / s.iloc[idx-20]) - 1.0) * 100.0) if idx >= 20 else chg_5d
                    
                    records.append({
                        "date": dt,
                        "ticker": ticker,
                        "close": round(val, 4),
                        "change_1d_pct": round(chg_1d, 2),
                        "change_5d_pct": round(chg_5d, 2),
                        "change_20d_pct": round(chg_20d, 2)
                    })
    
    if records:
        df = pd.DataFrame(records)
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("market_prices", conn, if_exists="replace", index=False)
        conn.close()
        print(f"Synced {len(records)} price records into SQLite database.")

def get_latest_snapshot():
    conn = sqlite3.connect(DB_PATH)
    prices_df = pd.read_sql_query("""
    SELECT ticker, close, change_1d_pct, change_5d_pct, change_20d_pct, date
    FROM market_prices
    WHERE date = (SELECT MAX(date) FROM market_prices)
    """, conn)
    
    # Also fetch previous date for any tickers missing in latest snapshot (e.g. crypto trades 24/7 vs US market)
    all_latest = pd.read_sql_query("""
    SELECT m1.ticker, m1.close, m1.change_1d_pct, m1.change_5d_pct, m1.change_20d_pct, m1.date
    FROM market_prices m1
    INNER JOIN (
        SELECT ticker, MAX(date) as max_date FROM market_prices GROUP BY ticker
    ) m2 ON m1.ticker = m2.ticker AND m1.date = m2.max_date
    """, conn)
    
    fred_latest = pd.read_sql_query("""
    SELECT f1.series_id, f1.value, f1.date
    FROM fred_observations f1
    INNER JOIN (
        SELECT series_id, MAX(date) as max_date FROM fred_observations GROUP BY series_id
    ) f2 ON f1.series_id = f2.series_id AND f1.date = f2.max_date
    """, conn)
    
    net_liq = pd.read_sql_query("SELECT * FROM net_liquidity ORDER BY date DESC LIMIT 1", conn)
    conn.close()
    
    return {
        "prices": all_latest.set_index("ticker").to_dict(orient="index"),
        "fred": fred_latest.set_index("series_id").to_dict(orient="index"),
        "net_liquidity": net_liq.to_dict(orient="records")[0] if not net_liq.empty else {}
    }

if __name__ == "__main__":
    init_db()
    print("Fetching FRED series...")
    sync_fred_data()
    print("Computing Fed Net Liquidity...")
    compute_net_liquidity()
    print("Fetching Market tickers...")
    sync_market_data()
    print("Testing latest snapshot...")
    snapshot = get_latest_snapshot()
    print("Snapshot summary:")
    print("Prices tickers count:", len(snapshot["prices"]))
    print("FRED indicators count:", len(snapshot["fred"]))
    print("Net Liquidity:", snapshot["net_liquidity"])
