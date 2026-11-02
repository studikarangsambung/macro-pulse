"""Snapshot rebuilt from the live page of 1 Nov 2026 (values and headlines as displayed)."""
import copy

def px(close, d1, d5=0.0, d20=0.0):
    return {"close": close, "change_1d_pct": d1, "change_5d_pct": d5, "change_20d_pct": d20}

SECTORS = {  # ticker: (close, 1D, 5D, 20D) from the scorecard
    "XLV": (184.87, .45, 3.12, 11.25), "XLE": (70.02, 1.91, 1.00, 11.46), "XLP": (89.42, 1.41, 1.31, 11.04),
    "XLU": (43.43, .67, 2.04, 9.04), "XLB": (52.74, .40, 2.79, 7.94), "XLRE": (43.17, .26, 1.41, 5.78),
    "XLF": (56.51, -.76, 1.09, 5.65), "XLY": (115.38, -.71, 2.02, 4.85), "XLI": (167.40, -1.60, 1.69, -1.50),
    "XLC": (99.90, -1.29, -5.32, -9.45), "XLK": (179.51, -4.89, -2.03, -10.16)}

def N(title, source, link="#"):
    return {"title": title, "source": source, "link": link}

NEWS = {
    "crypto": [
        N("Binance opens crypto withdrawals in phases starting with bitcoin following $6.3 billion hack", "CoinDesk"),
        N("Binance Lost Over $6 Billion in Crypto Hack. Here\u2019s What to Know.", "The New York Times"),
        N("Why bitcoin held up better after the record Binance hack", "CNBC"),
        N("\u725b\u6765 (Niu Lai) Price (\u725b\u6765/USD) Today | Live Price, Market Cap & Chart", "Binance"),
        N("Binance resumes bitcoin, ether withdrawals after covering bulk of stolen $6.3 billion", "Reuters"),
        N("Bitcoin BTC (BTC-USD) Live Price, News, Chart and Price History", "Yahoo Finance UK"),
    ],
    "gold": [
        N("Why Is Gold Going Down? Gold Falls 27% From Its Record", "CryptoTicker.io"),
        N("Gold prices break above USD 4,400\u2014can the precious metals ra... - Futubull Community", "\u5bcc\u9014\u725b\u725b"),
    ],
    "oil": [
        N("US Shale Stays in the Money Despite Oil Price Drop", "EnergyNow"),
        N("Will the US-Iran ceasefire bring down gas prices? - ABC News", "ABC News"),
        N("Saudi Arabia Cuts August Arab Light Asia OSP, Biggest Drop in Over Two Decades", "EnergyNow.com"),
    ],
    "dollar": [
        N("US Dollar Index Price Forecast: Lower Bond Yields Leave DXY Struggling Near 101.75", "www.tmgm.com"),
        N("Gold Falls. Bonds Rise. Why? for BITSTAMP:BTCUSD by BlueNyraFx", "TradingView"),
    ],
    "tech": [N("US tech stocks tumble as concerns over AI spending intensify", "Financial Times")],
    "indonesia": [
        N("Bank Indonesia catat pengguna QRIS di Sulawesi Tengah tumbuh 18,83 persen", "ANTARA News Sulteng"),
        N("BEI Uji Coba Penghapusan Saham HSC dari IHSG - Market", "Bloomberg Technoz"),
        N("Dihantam Sentimen Global dan Isu MSCI, IHSG Terkoreksi 16,23% di Oktober 2026", "kontan.co.id"),
    ],
}

def snapshot():
    prices = {
        "SPY": px(600, -1.77, 0, -3.0), "QQQ": px(500, -3.47, 0, -6.0),
        "BTC-USD": px(77835.67, 0.52, -3.67, -4.80), "ETH-USD": px(2260.38, 0.34, -3.72, -7.53),
        "SOL-USD": px(94.67, -0.71, -6.5, -10.32),
        "^TNX": px(4.929, -1.20), "^IRX": px(3.973, 0.0), "DX-Y.NYB": px(101.88, -0.16),
        "CL=F": px(104.12, 2.08, 0, 14.3), "GC=F": px(3875.4, -0.17, 0, -3.0),
        "^VIX": px(19.42, 1.0), "^JKSE": px(5057.05, -0.80, 0, -16.2),
        "USDIDR=X": px(18120, 0.27), "EIDO": px(9.96, -1.19),
    }
    for t, (c, d1, d5, d20) in SECTORS.items():
        prices[t] = px(c, d1, d5, d20)
    return {
        "prices": prices,
        "fred": {"DFII10": {"value": 2.63}, "BAMLH0A0HYM2": {"value": 3.26}},
        "net_liquidity": {"net_liquidity_bil": 5741.5, "change_4w_bil": -52.5},
        "news_by_category": copy.deepcopy(NEWS),
        "crypto_news": copy.deepcopy(NEWS["crypto"]),
    }
