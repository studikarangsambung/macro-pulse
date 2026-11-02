"""
driver_engine.py - single source of truth for "what moved" and "what news is related".

Replaces the text-template logic that used to live in
analytics_engine.analyze_market_drivers and in narrative_generator.

Principles (each one fixes a bug found in the live page):
  1. Describe moves from data (sign + magnitude). Never assert a cause.
     Headlines are shown as "berita terkait", not as the reason for a move.
  2. A headline is shown only if it matches the asset AND its tone does not
     contradict the move (e.g. an "oil price drop" story is not shown beside +2% oil).
  3. Missing data is reported as missing. No invented prices, headlines or sources.
  4. One threshold table (FLAT_BAND) is used by every module, so the dashboard,
     the sentiment chain and the WhatsApp text can never disagree on direction.
  5. Time labels (last trading session, H.4.1 release) are computed with real
     time zones, so they stay correct across DST changes.
"""

import datetime
import re
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")
NY = ZoneInfo("America/New_York")

# |1D change %| below the band is "datar". Yield uses relative % change.
FLAT_BAND = {
    "equity": 0.30,
    "oil": 0.80,
    "crypto": 1.00,
    "gold": 0.40,
    "fx": 0.20,
    "dollar": 0.20,
    "yield": 0.50,
}

# Net-liquidity 4-week change as % of the level (replaces the fixed +/-50bn cliff).
LIQ_DANGER_PCT = -1.0
LIQ_STRONG_PCT = 1.0

_DAYS_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
_MONTHS_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
              "Agustus", "September", "Oktober", "November", "Desember"]


# ----------------------------------------------------------------- data access
def get_px(prices, *tickers):
    """First ticker with a usable close. Returns None when data is missing."""
    for t in tickers:
        d = prices.get(t)
        if d and d.get("close"):
            return {
                "ticker": t,
                "close": d["close"],
                "chg_1d": d.get("change_1d_pct"),
                "chg_5d": d.get("change_5d_pct"),
                "chg_20d": d.get("change_20d_pct"),
            }
    return None


def classify_move(kind, chg):
    if chg is None:
        return None
    band = FLAT_BAND[kind]
    if chg > band:
        return "naik"
    if chg < -band:
        return "turun"
    return "datar"


def pct(x, nd=2):
    return "n/a" if x is None else f"{x:+.{nd}f}%"


def yield_change_bp(close, chg_pct):
    """Convert ^TNX relative % change into basis points."""
    if close is None or chg_pct is None:
        return None
    prev = close / (1 + chg_pct / 100.0)
    return (close - prev) * 100.0


def liquidity_state(level_bil, chg_4w_bil):
    """Returns (label, ews_status). Used by BOTH the EWS and the broadcast."""
    if not level_bil:
        return "Data tidak tersedia", None
    p = chg_4w_bil / level_bil * 100.0
    if p >= LIQ_STRONG_PCT:
        return "Ekspansi Kuat", "AMAN"
    if p > 0:
        return "Ekspansi Moderat", "AMAN"
    if p > LIQ_DANGER_PCT:
        return "Kontraksi Ringan", "WASPADA"
    return "Kontraksi Tegas", "BAHAYA"


# ------------------------------------------------------------------------ time
def fmt_id_date(d):
    return f"{_DAYS_ID[d.weekday()]}, {d.day} {_MONTHS_ID[d.month - 1]} {d.year}"


def last_us_session_date(now=None):
    """Date of the most recent completed Wall Street session (holidays ignored)."""
    t = (now or datetime.datetime.now(WIB)).astimezone(NY)
    d = t.date()
    if not (t.weekday() < 5 and t.hour >= 16):
        d -= datetime.timedelta(days=1)
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    return d


def h41_release_text(now=None):
    """Next Fed H.4.1 release (Thursday 16:30 New York) expressed in WIB."""
    t = (now or datetime.datetime.now(WIB)).astimezone(NY)
    cand = (t + datetime.timedelta(days=(3 - t.weekday()) % 7)).replace(
        hour=16, minute=30, second=0, microsecond=0)
    if cand <= t:
        cand += datetime.timedelta(days=7)
    w = cand.astimezone(WIB)
    return f"{_DAYS_ID[w.weekday()]} ~{w:%H:%M} WIB ({cand:%H:%M} {cand.tzname()})"


# ------------------------------------------------------------------------ news
ASSET_KEYWORDS = {
    "gold": ["gold", "xau", "bullion", "emas"],
    "oil": ["oil", "crude", "wti", "brent", "opec", "minyak", "gasoline", "refinery"],
    "crypto": ["bitcoin", "btc", "crypto", "ether", "ethereum", "binance", "etf",
               "stablecoin", "solana"],
    "dollar": ["dollar", "dxy", "yield", "yields", "treasury", "treasuries", "fed",
               "bond", "bonds", "rate", "rates", "inflation"],
    "tech": ["nasdaq", "tech", "s&p", "wall street", "stocks", "stock", "ai",
             "chip", "chips", "earnings"],
    "indonesia": ["ihsg", "rupiah", "bank indonesia", "bei", "idx", "msci", "ojk",
                  "saham", "hsc", "bi-rate", "apbn"],
}

NOISE_TITLE = re.compile(
    r"live price|price today|market cap|price history|price chart|"
    r"\brates? today\b|\brates? in \w+|\bjewellery\b|\b22k\b|\b24k\b|"
    r"\bgarden city\b|\bper gram\b|\brate in [a-z]+\b|"
    r"\bfor [A-Z0-9]+:[A-Z0-9]+\b|\(btc-usd\)", re.I)
NOISE_SOURCES = {"tradingview"}

_NEG = re.compile(
    r"\b(drop|drops|dropped|fall|falls|fell|plunge|plunges|plunged|slump|slumps|"
    r"tumble|tumbles|sink|sinks|slide|slides|decline|declines|lower|sell-off|"
    r"selloff|turun|anjlok|melemah|terkoreksi|jatuh|cut|cuts|cutting|slashed|slashing|"
    r"dip|dips|losses|loses|retreats|retreating|down)\b", re.I)
_POS = re.compile(
    r"\b(rise|rises|rose|surge|surges|surged|jump|jumps|rally|rallies|climb|"
    r"climbs|gain|gains|higher|rebound|rebounds|record high|naik|melonjak|"
    r"menguat|reli|raising|raise|raises|boost|boosts|spike|spikes|spiked|up)\b", re.I)
_STOP = {"the", "and", "for", "with", "from", "after", "over", "here", "what", "know",
         "why", "how", "that", "this", "its", "are", "has", "have", "will", "not",
         "new", "into", "amid", "than", "dan", "yang", "untuk", "dari", "pada"}


def headline_tone(title):
    n, p = len(_NEG.findall(title)), len(_POS.findall(title))
    return "neg" if n > p else "pos" if p > n else None


def _mostly_latin(s, thr=0.85):
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return False
    latin = sum(1 for c in letters if c.isascii() or "\u00c0" <= c <= "\u024f")
    return latin / len(letters) >= thr


def _tokens(s):
    return {w for w in re.findall(r"[a-z0-9]{3,}", s.lower()) if w not in _STOP}


def same_event(a, b):
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    shared = len(ta & tb)
    return shared >= 3 or shared / len(ta | tb) >= 0.5


def _kw_hits(title, kws):
    t = title.lower()
    return sum(1 for k in kws if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t))


def pick_news(items, kind, move_state=None, limit=1):
    """Relevant, non-noise, tone-compatible, de-duplicated headlines (best first)."""
    kws = ASSET_KEYWORDS[kind]
    scored, kept_titles = [], []
    for idx, it in enumerate(items or []):
        title = (it.get("title") or "").strip()
        src = (it.get("source") or "").strip()
        if not title or not _mostly_latin(title):
            continue
        if NOISE_TITLE.search(title) or src.lower() in NOISE_SOURCES:
            continue
        hits = _kw_hits(title, kws)
        if hits == 0:
            continue
        tone = headline_tone(title)
        if (move_state == "naik" and tone == "neg") or (move_state == "turun" and tone == "pos"):
            continue
        if any(same_event(title, k) for k in kept_titles):
            continue
        kept_titles.append(title)
        scored.append((-hits, idx, it))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [s[2] for s in scored[:limit]]


def _news_ref(it):
    if not it:
        return {"title": "", "source": "", "link": "#", "available": False}
    return {"title": it.get("title", ""), "source": it.get("source", ""),
            "link": it.get("link", "#"), "available": True}


def _news_sentence(ref):
    if ref["available"]:
        return f"Berita pasar terkait: \"{ref['title']}\" ({ref['source']})."
    return "Tidak ada berita relevan yang selaras arah di feed saat ini."


# --------------------------------------------------------------- co-movements
def co_phrase(asset_state, partner, partner_state, partner_text, inverse=False):
    """Say whether a partner asset moved the way it typically does. No causal verbs."""
    if asset_state in (None, "datar") or partner_state in (None, "datar"):
        return ""
    same = asset_state == partner_state
    typical = (not same) if inverse else same
    tag = "sejalan dengan pola tipikal" if typical else "berlawanan dengan pola tipikal"
    return f"{partner} {partner_text} ({tag})"


def _fmt_move(chg1, chg20):
    s = f"1D {pct(chg1)}"
    if chg20 is not None:
        s += f", 20D {pct(chg20, 1)}"
    return s


_VERB = {"naik": "naik", "turun": "turun", "datar": "bergerak datar", None: "tanpa data"}


def _unavailable(name):
    return {"available": False, "state": None, "driver": f"Data {name} tidak tersedia.",
            "tag": "Data tidak tersedia", "summary": f"Data {name} tidak tersedia.",
            "news": _news_ref(None)}


# ----------------------------------------------------------------- main entry
def analyze_market_drivers(snapshot, regime_text=None):
    prices = snapshot.get("prices", {})
    news_cat = snapshot.get("news_by_category", {})

    def pool(key, *fallback_keys):
        items = list(news_cat.get(key, []))
        for fk in fallback_keys:
            items += snapshot.get(fk, [])
        return items

    tnx = get_px(prices, "^TNX")
    dxy = get_px(prices, "DX-Y.NYB")
    qqq = get_px(prices, "QQQ")
    spy = get_px(prices, "SPY")
    tnx_bp = yield_change_bp(tnx["close"], tnx["chg_1d"]) if tnx else None
    tnx_state = classify_move("yield", tnx["chg_1d"]) if tnx else None
    dxy_state = classify_move("dollar", dxy["chg_1d"]) if dxy else None
    bp_text = f"{tnx_bp:+.1f} bp" if tnx_bp is not None else "n/a"

    out = {}

    # ---- gold
    g = get_px(prices, "GC=F")
    if not g:
        out["gold"] = _unavailable("emas")
    else:
        st = classify_move("gold", g["chg_1d"])
        news = _news_ref((pick_news(pool("gold"), "gold", st) or [None])[0])
        co = [c for c in (
            co_phrase(st, "yield 10Y", tnx_state, bp_text, inverse=True) if tnx else "",
            co_phrase(st, "DXY", dxy_state, pct(dxy["chg_1d"]) if dxy else "", inverse=True) if dxy else "",
        ) if c]
        out["gold"] = {
            "available": True, "state": st, "price": g["close"],
            "chg_1d": g["chg_1d"], "chg_20d": g["chg_20d"],
            "tag": f"Emas {_VERB[st]}",
            "driver": (f"Emas spot {_VERB[st]} ke US$ {g['close']:,.1f}/oz ({_fmt_move(g['chg_1d'], g['chg_20d'])}). "
                       + (("Pasangan: " + "; ".join(co) + ". ") if co else "")
                       + _news_sentence(news)),
            "summary": f"Emas {_VERB[st]} ({pct(g['chg_1d'])} 1D, {pct(g['chg_20d'], 1)} 20D)",
            "news": news,
        }

    # ---- oil
    o = get_px(prices, "CL=F")
    if not o:
        out["oil"] = _unavailable("minyak WTI")
    else:
        st = classify_move("oil", o["chg_1d"])
        news = _news_ref((pick_news(pool("oil", "geopolitics_news"), "oil", st) or [None])[0])
        out["oil"] = {
            "available": True, "state": st, "price": o["close"],
            "chg_1d": o["chg_1d"], "chg_20d": o["chg_20d"],
            "tag": f"Minyak {_VERB[st]}",
            "driver": (f"Minyak WTI {_VERB[st]} ke US$ {o['close']:.2f}/barel ({_fmt_move(o['chg_1d'], o['chg_20d'])}). "
                       + _news_sentence(news)),
            "summary": f"Minyak {_VERB[st]} ({pct(o['chg_1d'])} 1D, {pct(o['chg_20d'], 1)} 20D)",
            "news": news,
        }

    # ---- crypto
    b = get_px(prices, "BTC-USD")
    if not b:
        out["crypto"] = _unavailable("Bitcoin")
    else:
        st = classify_move("crypto", b["chg_1d"])
        q_state = classify_move("equity", qqq["chg_1d"]) if qqq else None
        news = _news_ref((pick_news(pool("crypto", "crypto_news"), "crypto", st) or [None])[0])
        co = co_phrase(st, "QQQ", q_state, pct(qqq["chg_1d"]) if qqq else "", inverse=False) if qqq else ""
        trend = ""
        if b["chg_20d"] is not None and b["chg_20d"] <= -3 and st != "turun":
            trend = f"Tren 20D masih negatif ({pct(b['chg_20d'], 1)}) walau 1D {_VERB[st]}. "
        out["crypto"] = {
            "available": True, "state": st, "price": b["close"],
            "chg_1d": b["chg_1d"], "chg_20d": b["chg_20d"],
            "tag": f"Bitcoin {_VERB[st]}",
            "driver": (f"Bitcoin {_VERB[st]} ke US$ {b['close']:,.0f} ({_fmt_move(b['chg_1d'], b['chg_20d'])}). "
                       + trend + ((co + ". ") if co else "") + _news_sentence(news)),
            "summary": f"Bitcoin {_VERB[st]} ({pct(b['chg_1d'])} 1D, {pct(b['chg_20d'], 1)} 20D)",
            "news": news,
        }

    # ---- dollar & yield
    if not tnx and not dxy:
        out["dollar"] = _unavailable("DXY/US10Y")
    else:
        st = tnx_state or dxy_state
        news = _news_ref((pick_news(pool("dollar"), "dollar", tnx_state) or [None])[0])
        parts = []
        if tnx:
            parts.append(f"US 10Y Yield {_VERB[tnx_state]} ke {tnx['close']:.3f}% ({bp_text} 1D)")
        if dxy:
            parts.append(f"DXY {dxy['close']:.2f} ({pct(dxy['chg_1d'])}, {_VERB[dxy_state]})")
        out["dollar"] = {
            "available": True, "state": st,
            "dxy": dxy["close"] if dxy else None, "chg_1d": dxy["chg_1d"] if dxy else None,
            "tnx": tnx["close"] if tnx else None, "tnx_1d": tnx["chg_1d"] if tnx else None,
            "tnx_bp": tnx_bp,
            "tag": f"Yield {_VERB[tnx_state]}, DXY {_VERB[dxy_state]}",
            "driver": "; ".join(parts) + ". " + _news_sentence(news),
            "summary": "; ".join(parts),
            "news": news,
        }

    # ---- US equities
    if not qqq and not spy:
        out["tech"] = _unavailable("QQQ/SPY")
    else:
        qs = classify_move("equity", qqq["chg_1d"]) if qqq else None
        ss = classify_move("equity", spy["chg_1d"]) if spy else None
        st = qs if qs == ss or ss is None else ss if qs is None else "beragam"
        move_for_news = st if st in ("naik", "turun") else None
        news = _news_ref((pick_news(pool("tech", "global_news"), "tech", move_for_news) or [None])[0])
        parts = []
        if qqq:
            parts.append(f"QQQ {pct(qqq['chg_1d'])}")
        if spy:
            parts.append(f"SPY {pct(spy['chg_1d'])}")
        out["tech"] = {
            "available": True, "state": st,
            "qqq": qqq["close"] if qqq else None, "qqq_1d": qqq["chg_1d"] if qqq else None,
            "spx": spy["close"] if spy else None, "spx_1d": spy["chg_1d"] if spy else None,
            "tag": f"Wall Street {_VERB.get(st, 'beragam')}",
            "driver": f"Wall Street {_VERB.get(st, 'beragam')} ({', '.join(parts)} 1D). " + _news_sentence(news),
            "summary": f"Wall Street {_VERB.get(st, 'beragam')} ({', '.join(parts)} 1D)",
            "news": news,
        }

    # ---- Indonesia
    ih = get_px(prices, "^JKSE")
    idr = get_px(prices, "USDIDR=X", "IDR=X")
    eido = get_px(prices, "EIDO")
    if not ih and not idr:
        out["indonesia"] = _unavailable("IHSG/USDIDR")
    else:
        ih_state = classify_move("equity", ih["chg_1d"]) if ih else None
        idr_state = classify_move("fx", idr["chg_1d"]) if idr else None
        deep = bool(ih and ih["chg_20d"] is not None and ih["chg_20d"] <= -8)
        news = _news_ref((pick_news(pool("indonesia", "indonesia_news"), "indonesia",
                                    ih_state if ih_state in ("naik", "turun") else None) or [None])[0])
        parts = []
        if ih:
            parts.append(f"IHSG {_VERB[ih_state]} ke {ih['close']:,.2f} ({_fmt_move(ih['chg_1d'], ih['chg_20d'])})")
        if idr:
            parts.append(f"USD/IDR Rp {idr['close']:,.0f} ({pct(idr['chg_1d'])} 1D)")
        if eido:
            parts.append(f"EIDO {pct(eido['chg_1d'])} (proksi minat asing, bukan data arus langsung)")
        co = co_phrase(idr_state, "DXY", dxy_state, pct(dxy["chg_1d"]) if dxy else "", inverse=False) if (idr and dxy) else ""
        if co.endswith("berlawanan dengan pola tipikal)"):
            co += " - kemungkinan faktor domestik/spesifik rupiah"
        extra = ""
        if deep:
            extra = (f"Penurunan 20D ({pct(ih['chg_20d'], 1)}) jauh lebih besar daripada 1D; "
                     "periksa faktor domestik (indeks, MSCI, regulasi) sebelum menyalahkan faktor global. ")
        out["indonesia"] = {
            "available": True, "state": ih_state,
            "ihsg": ih["close"] if ih else None, "ihsg_1d": ih["chg_1d"] if ih else None,
            "ihsg_20d": ih["chg_20d"] if ih else None,
            "usdidr": idr["close"] if idr else None, "usdidr_1d": idr["chg_1d"] if idr else None,
            "tag": "Koreksi dalam (20D)" if deep else f"IHSG {_VERB[ih_state]}",
            "driver": "; ".join(parts) + ". " + extra + ((co + ". ") if co else "") + _news_sentence(news),
            "summary": "; ".join(parts[:2]),
            "news": news,
        }

    # ---- Fed liquidity
    nl = snapshot.get("net_liquidity", {})
    lvl, chg = nl.get("net_liquidity_bil", 0), nl.get("change_4w_bil", 0)
    label, _ = liquidity_state(lvl, chg)
    pct_chg = (chg / lvl * 100.0) if lvl else None
    out["fed"] = {
        "net_liq": lvl, "chg_4w": chg, "label": label,
        "driver": (f"Likuiditas Bersih The Fed US$ {lvl:,.1f} Miliar (4 pekan: {chg:+.1f} Miliar"
                   f"{'' if pct_chg is None else f', {pct_chg:+.2f}% dari level'}) - {label}. "
                   f"Rilis H.4.1 berikutnya: {h41_release_text()}. "
                   "Perubahan neto dipengaruhi saldo TGA dan RRP."),
    }

    out["regime"] = {"title": (snapshot.get("_regime_title") or ""), "driver": regime_text or ""}
    return out
