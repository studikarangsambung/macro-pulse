"""
Configuration & Metadata for US Sectors & Crypto Macro Monitor Engine
"""

FRED_API_KEY = "99c703d28398c06080d7437d00040ae4"

# FRED Series IDs
FRED_SERIES = {
    "WALCL": "Fed Total Assets (Mil $)",
    "WTREGEN": "Treasury General Account TGA (Mil $)",
    "RRPONTSYD": "Overnight Reverse Repo RRP (Bil $)",
    "DFII10": "10-Year Real Interest Rate TIPS (%)",
    "BAMLH0A0HYM2": "US High Yield Option-Adjusted Spread (%)",
    "NFCI": "Chicago Fed Financial Conditions Index",
}

# Market Tickers (Yahoo Finance)
TICKERS_MACRO = {
    "^TNX": "US 10Y Treasury Yield",
    "^IRX": "US 3M T-Bill Yield",
    "^TYX": "US 30Y Treasury Yield",
    "DX-Y.NYB": "US Dollar Index (DXY)",
    "^VIX": "CBOE Volatility Index",
    "CL=F": "WTI Crude Oil ($/bbl)",
    "GC=F": "Emas / XAUUSD ($/oz)",
    "USDIDR=X": "USD / IDR (Rupiah)",
    "EIDO": "iShares MSCI Indonesia ETF",
    "HG=F": "Copper Futures ($/lb)",
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq 100 ETF",
}

TICKERS_SECTORS = {
    "XLK": {"name": "Technology", "profile": "High Beta / Long Duration", "best_in": "Disinflationary Boom"},
    "XLC": {"name": "Communication Services", "profile": "High Beta / Ad Cyclical", "best_in": "Early/Mid Cycle"},
    "XLY": {"name": "Consumer Discretionary", "profile": "Consumer Health / Rate Sensitive", "best_in": "Early Recovery"},
    "XLF": {"name": "Financials", "profile": "Yield Curve Steepening / Credit", "best_in": "Reflation / Steepener"},
    "XLE": {"name": "Energy", "profile": "Inflation Hedge / Commodity Shock", "best_in": "Stagflation / Reflation"},
    "XLI": {"name": "Industrials", "profile": "Global Trade / Capex Cycle", "best_in": "Mid Cycle Expansion"},
    "XLB": {"name": "Materials", "profile": "Commodity / Infrastructure", "best_in": "Reflation"},
    "XLV": {"name": "Health Care", "profile": "Defensive / Non-cyclical", "best_in": "Late Cycle / Contraction"},
    "XLP": {"name": "Consumer Staples", "profile": "Defensive / Margin Squeeze", "best_in": "Contraction / Stagflation"},
    "XLU": {"name": "Utilities", "profile": "Bond Proxy / AI Power Demand", "best_in": "Contraction / Falling Yields"},
    "XLRE": {"name": "Real Estate", "profile": "Debt Burden / Yield Sensitive", "best_in": "Falling Yields / Recovery"},
}

TICKERS_CRYPTO = {
    "BTC-USD": {"name": "Bitcoin", "category": "Digital Gold / High Beta Liquidity"},
    "ETH-USD": {"name": "Ethereum", "category": "Smart Contract / Tech Platform"},
    "SOL-USD": {"name": "Solana", "category": "High Throughput / Speculative Beta"},
}

# EWS (Early Warning System) Thresholds
EWS_THRESHOLDS = {
    "VIX_ELEVATED": 20.0,
    "VIX_PANIC": 30.0,
    "HY_SPREAD_WIDENING": 400.0,  # bps
    "HY_SPREAD_STRESS": 550.0,    # bps
    "REAL_YIELD_TIGHT": 2.0,      # % (DFII10 above 2% stresses risk assets)
    "US10Y_CRITICAL": 4.80,       # %
}

DB_PATH = "data/macro_vault.db"
