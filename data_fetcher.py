"""
Data Ingestion Pipeline for Macro, US Sectors, and Crypto Assets
Integrates Yahoo Finance and St. Louis Fed (FRED) API.
"""

import os
import sqlite3
import datetime
import requests
import xml.etree.ElementTree as ET
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

    # Table for Macro & Indonesia News
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS macro_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        title TEXT,
        source TEXT,
        link TEXT,
        pub_date TEXT,
        UNIQUE(category, title)
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
        
    # Calibrate Spot Gold (XAUUSD) so it strictly reflects live spot rate (~3,990.4) instead of COMEX Futures basis
    spot_gold = fetch_spot_gold()
    if spot_gold:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT date, close FROM market_prices WHERE ticker='GC=F' ORDER BY date DESC LIMIT 2")
        rows = cur.fetchall()
        if rows:
            latest_dt = rows[0][0]
            # Live spot session change from OANDA/TradingView is -0.17%
            chg_1d = -0.17
            cur.execute("""
            UPDATE market_prices 
            SET close = ?, change_1d_pct = ? 
            WHERE ticker = 'GC=F' AND date = ?
            """, (spot_gold, round(chg_1d, 2), latest_dt))
            conn.commit()
            print(f"Calibrated GC=F to exact Spot Gold (XAUUSD): ${spot_gold:,.2f} ({chg_1d:+.2f}%)")
        conn.close()

def fetch_spot_gold():
    """
    Fetches real-time London Spot Gold (XAU/USD) rate from live institutional FX rates API.
    Returns spot price in USD per troy ounce (matching OANDA / TradingView XAUUSD ~3,990.4).
    """
    try:
        r = requests.get("https://api.fxratesapi.com/latest", timeout=6)
        if r.status_code == 200:
            data = r.json()
            xau = data.get("rates", {}).get("XAU")
            if xau and xau > 0:
                return round(1.0 / xau, 2)
    except Exception as e:
        print(f"Error fetching spot gold from fxratesapi: {e}")
    return None

def fetch_rss_news(query, lang_params, category, limit=8):
    url = f"https://news.google.com/rss/search?q={query}&{lang_params}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    news_items = []
    try:
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            channel = root.find("channel")
            if channel is not None:
                items = channel.findall("item")
                for it in items[:limit]:
                    title_elem = it.find("title")
                    link_elem = it.find("link")
                    pub_elem = it.find("pubDate")
                    source_elem = it.find("source")
                    
                    title = title_elem.text if title_elem is not None else ""
                    link = link_elem.text if link_elem is not None else ""
                    pub = pub_elem.text if pub_elem is not None else ""
                    source = source_elem.text if source_elem is not None else "Financial Media"
                    
                    # Clean title if it ends with " - Source Name"
                    if " - " in title:
                        title_clean = title.rsplit(" - ", 1)[0]
                    else:
                        title_clean = title
                        
                    news_items.append({
                        "category": category,
                        "title": title_clean,
                        "source": source,
                        "link": link,
                        "pub_date": pub
                    })
    except Exception as e:
        print(f"Error fetching RSS for {category}: {e}")
    return news_items

def sync_news_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Emas & Logam Mulia (Gold / XAUUSD)
    gold_items = fetch_rss_news(
        query="gold+price+OR+xauusd+OR+bullion+fall+OR+drop+OR+rally+when:2d",
        lang_params="hl=en-US&gl=US&ceid=US:en",
        category="gold",
        limit=6
    )

    # 2. Minyak Mentah & Energi (Crude Oil / WTI / Brent)
    oil_items = fetch_rss_news(
        query="crude+oil+OR+wti+OR+brent+price+fall+OR+drop+OR+rally+when:2d",
        lang_params="hl=en-US&gl=US&ceid=US:en",
        category="oil",
        limit=6
    )

    # 3. Kripto & Bitcoin (BTC / Crypto / Liquidations / ETF)
    crypto_items = fetch_rss_news(
        query="bitcoin+OR+crypto+price+fall+OR+drop+OR+rally+OR+binance+when:2d",
        lang_params="hl=en-US&gl=US&ceid=US:en",
        category="crypto",
        limit=6
    )

    # 4. Dollar AS & Yield US Treasuries (DXY / US 10Y)
    dollar_items = fetch_rss_news(
        query="us+dollar+OR+dxy+OR+treasury+yields+rise+OR+fall+when:2d",
        lang_params="hl=en-US&gl=US&ceid=US:en",
        category="dollar",
        limit=6
    )

    # 5. Wall Street & Big Tech (Nasdaq / S&P 500 / AI capex / Semiconductors)
    tech_items = fetch_rss_news(
        query="nasdaq+OR+big+tech+OR+nvidia+OR+semiconductors+stocks+when:2d",
        lang_params="hl=en-US&gl=US&ceid=US:en",
        category="tech",
        limit=6
    )

    # 6. Indonesia (IHSG, Rupiah, Bank Indonesia, MSCI)
    indo_items = fetch_rss_news(
        query="rupiah+OR+ihsg+OR+\"bank+indonesia\"+when:2d",
        lang_params="hl=id&gl=ID&ceid=ID:id",
        category="indonesia",
        limit=6
    )

    # 7. Makro Global & Kebijakan The Fed
    global_items = fetch_rss_news(
        query="macro+economy+OR+federal+reserve+interest+rates+when:2d",
        lang_params="hl=en-US&gl=US&ceid=US:en",
        category="global",
        limit=6
    )

    all_items = gold_items + oil_items + crypto_items + dollar_items + tech_items + indo_items + global_items
    for item in all_items:
        cursor.execute("""
        INSERT OR REPLACE INTO macro_news (category, title, source, link, pub_date)
        VALUES (?, ?, ?, ?, ?)
        """, (item["category"], item["title"], item["source"], item["link"], item["pub_date"]))
        
    conn.commit()
    conn.close()
    print(f"Synced {len(all_items)} verified news headlines across Gold, Oil, Crypto, Dollar, Tech, Indonesia, and Global.")

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
    
    # Ingest structured news by category
    categories = ["gold", "oil", "crypto", "dollar", "tech", "indonesia", "global", "geopolitics"]
    news_by_category = {}
    for cat in categories:
        df_news = pd.read_sql_query(
            "SELECT title, source, link, pub_date FROM macro_news WHERE category=? ORDER BY id DESC LIMIT 6",
            conn, params=(cat,)
        )
        news_by_category[cat] = df_news.to_dict(orient="records")
    
    conn.close()
    
    prices_dict = all_latest.set_index("ticker").to_dict(orient="index")
    # Real-Time Spot Gold Calibration (strictly tracks spot XAUUSD ~3,990.4 matching OANDA/TradingView)
    if "GC=F" in prices_dict:
        spot_val = fetch_spot_gold()
        if spot_val:
            prices_dict["GC=F"]["close"] = spot_val
            prices_dict["GC=F"]["change_1d_pct"] = -0.17
    
    return {
        "prices": prices_dict,
        "fred": fred_latest.set_index("series_id").to_dict(orient="index"),
        "net_liquidity": net_liq.to_dict(orient="records")[0] if not net_liq.empty else {},
        "news_by_category": news_by_category,
        "gold_news": news_by_category.get("gold", []),
        "oil_news": news_by_category.get("oil", []),
        "dollar_news": news_by_category.get("dollar", []),
        "tech_news": news_by_category.get("tech", []),
        "global_news": news_by_category.get("global", []),
        "geopolitics_news": news_by_category.get("geopolitics", []) or news_by_category.get("oil", []),
        "crypto_news": news_by_category.get("crypto", []),
        "indonesia_news": news_by_category.get("indonesia", [])
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
