"""Test stub for the project's config.py (only what analytics_engine imports)."""
DB_PATH = ":memory:"
EWS_THRESHOLDS = {
    "US10Y_CRITICAL": 4.5, "REAL_YIELD_TIGHT": 2.0,
    "HY_SPREAD_STRESS": 500, "HY_SPREAD_WIDENING": 400,
    "VIX_PANIC": 30, "VIX_ELEVATED": 20,
}
TICKERS_SECTORS = {t: {"name": n, "profile": "test"} for t, n in [
    ("XLK", "Technology"), ("XLE", "Energy"), ("XLB", "Materials"), ("XLF", "Financials"),
    ("XLV", "Health Care"), ("XLP", "Consumer Staples"), ("XLU", "Utilities"),
    ("XLRE", "Real Estate"), ("XLY", "Consumer Discretionary"), ("XLI", "Industrials"),
    ("XLC", "Communication Services")]}
TICKERS_CRYPTO = {"BTC-USD": {"name": "Bitcoin", "category": "x"}}
