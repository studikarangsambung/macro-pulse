"""
Narrative & Causality Chain Generator  (patched)
Generates:
1. Copy-paste ready WhatsApp / Telegram Macro & Sector Impact Broadcast
2. Executive Summary payload for the HTML Dashboard

What changed vs. the previous version (see inline "FIX" notes):
  * Direction words come from driver_engine.classify_move - the SAME thresholds as the
    dashboard cards - so a title can no longer say "konsolidasi" while the text under it
    says "likuidasi", or "koreksi" next to a positive move.
  * No hard-coded fallback numbers, headlines or source names.
  * "Update Perdagangan: <hari ini>" -> last completed Wall Street session.
  * H.4.1 release time computed with real time zones (DST-safe).
  * Sector labels: "Sektor Terkuat / Terlemah" (the old "Sektor Defensif" simply
    relabelled the two best performers, which is how XLE ended up "defensif").
"""

import datetime

from driver_engine import (
    analyze_market_drivers, classify_move, fmt_id_date, get_px, h41_release_text,
    last_us_session_date, liquidity_state, pick_news, pct,
)

WIB_TZ = datetime.timezone(datetime.timedelta(hours=7))


def get_wib_now():
    return datetime.datetime.now(WIB_TZ)


_UD = {"naik": "naik", "turun": "turun", "datar": "bergerak datar",
       "beragam": "bergerak beragam", None: "tanpa data"}


def _news_line(drv):
    n = (drv or {}).get("news") or {}
    if n.get("available"):
        return f"↳ Berita terkait: {n['title']} ({n['source']})"
    return None


def build_validated_sentiment_chain(prices, sectors, snapshot, market_drivers=None):
    """
    Five-stage chain. Titles/directions derive only from market_drivers states (one threshold
    table). Headlines are labelled "Berita terkait" and never presented as the cause.
    """
    md = market_drivers or analyze_market_drivers(snapshot)
    blocks = []

    # 1-2. Wall Street and sectors
    qqq, spy = get_px(prices, "QQQ"), get_px(prices, "SPY")
    if qqq and spy:
        tech = md.get("tech", {})
        stage1 = [f"Ekuitas AS {_UD.get(tech.get('state'), 'bergerak beragam')}"]
        if _news_line(tech):
            stage1.append(_news_line(tech))
        blocks.append("\n".join(stage1))

        stage2 = [f"Nasdaq (QQQ {pct(qqq['chg_1d'])}) & S&P 500 (SPY {pct(spy['chg_1d'])})."]
        valid = [s for s in (sectors or []) if s.get("chg_1d") is not None]
        if len(valid) >= 4:
            ranked = sorted(valid, key=lambda s: s["chg_1d"], reverse=True)
            fmt = lambda xs: ", ".join(f"{s['ticker']} {s['chg_1d']:+.2f}%" for s in xs)
            stage2.append(f"Sektor Terkuat: {fmt(ranked[:2])}")
            stage2.append(f"Sektor Terlemah: {fmt(ranked[-2:])}")
        blocks.append("\n".join(stage2))
    else:
        blocks.append("Ekuitas AS: data QQQ/SPY tidak tersedia")

    # 3. Oil
    oil = md.get("oil", {})
    if oil.get("available"):
        s3 = [f"Minyak Mentah {_UD[oil['state']].capitalize()}"]
        if _news_line(oil):
            s3.append(_news_line(oil))
        s3.append(f"Minyak WTI US$ {oil['price']:.2f} / barel (1D {pct(oil['chg_1d'])}, 20D {pct(oil['chg_20d'], 1)})")
        blocks.append("\n".join(s3))
    else:
        blocks.append("Minyak: data tidak tersedia")

    # 4. Crypto
    parts = []
    for tk, lab, fmt_p in (("BTC-USD", "BTC", "{:,.0f}"), ("ETH-USD", "ETH", "{:,.0f}"), ("SOL-USD", "SOL", "{:.2f}")):
        px = get_px(prices, tk)
        parts.append(f"{lab} US$ {fmt_p.format(px['close'])} ({pct(px['chg_1d'])})" if px else f"{lab} n/a")
    cr = md.get("crypto", {})
    if cr.get("available"):
        s4 = [f"Pasar Kripto: Bitcoin {_UD[cr['state']]}", ", ".join(parts)]
        if cr.get("chg_20d") is not None and cr["chg_20d"] <= -3 and cr["state"] != "turun":
            s4.append(f"Tren 20D BTC masih negatif ({pct(cr['chg_20d'], 1)})")
        if _news_line(cr):
            s4.append(_news_line(cr))
        blocks.append("\n".join(s4))
    else:
        blocks.append("Pasar Kripto: data tidak tersedia")

    # 5. Yield, dollar, gold
    s5 = ["Yield, Dollar & Emas"]
    dol, gold = md.get("dollar", {}), md.get("gold", {})
    s5.append(dol.get("summary") or "Data yield/DXY tidak tersedia")
    if _news_line(dol):
        s5.append(_news_line(dol))
    if gold.get("available"):
        s5.append(f"Emas Spot US$ {gold['price']:,.1f} / troy oz ({pct(gold['chg_1d'])} 1D, {pct(gold['chg_20d'], 1)} 20D)")
        if _news_line(gold):
            s5.append(_news_line(gold))
    else:
        s5.append("Emas: data tidak tersedia")
    blocks.append("\n".join(s5))

    return "\n↓\n".join(blocks)


def _price_line(label, px, fmt="{:,.0f}"):
    if not px:
        return f"• {label}: data tidak tersedia"
    return f"• {label}: US$ {fmt.format(px['close'])} (1D: {pct(px['chg_1d'])})"


def generate_whatsapp_broadcast(snapshot, ews_signals, regime, corrs, sectors, crypto_data,
                                eth_btc_ratio, indo_macro=None, weekly_calendar=None,
                                flow_proj=None, market_drivers=None):
    wib_now = get_wib_now()
    # FIX: label the data date, not the day the script happened to run (it said "Minggu").
    session_str = fmt_id_date(last_us_session_date(wib_now))
    prepared_str = f"{fmt_id_date(wib_now.date())} {wib_now:%H:%M} WIB"

    prices = snapshot.get("prices", {})
    net_liq = snapshot.get("net_liquidity", {})
    md = market_drivers or analyze_market_drivers(snapshot)

    btc, eth, sol = get_px(prices, "BTC-USD"), get_px(prices, "ETH-USD"), get_px(prices, "SOL-USD")

    # Net liquidity (same rule as the EWS)
    nl_val, nl_chg = net_liq.get("net_liquidity_bil", 0), net_liq.get("change_4w_bil", 0)
    liq_label, _ = liquidity_state(nl_val, nl_chg)
    liq_pct = f", {nl_chg / nl_val * 100:+.2f}% dari level" if nl_val else ""

    if not eth_btc_ratio:
        altseason_status = "Data ETH/BTC tidak tersedia"
    elif eth_btc_ratio < 0.035:
        altseason_status = f"Dominasi Bitcoin Kuat (Altseason Tertahan) [Rasio ETH/BTC: {eth_btc_ratio:.4f}]"
    elif eth_btc_ratio < 0.05:
        altseason_status = f"Konsolidasi Pasangan ETH/BTC [Rasio ETH/BTC: {eth_btc_ratio:.4f}]"
    else:
        altseason_status = f"Altseason Aktif (Likuiditas Meluas ke Altcoins) [Rasio ETH/BTC: {eth_btc_ratio:.4f}]"

    chain_section = build_validated_sentiment_chain(prices, sectors, snapshot, md)

    # FIX: relevant, de-duplicated by event, no invented bullet when the feed is empty.
    crypto_pool = list(snapshot.get("news_by_category", {}).get("crypto", [])) or list(snapshot.get("crypto_news", []))
    crypto_items = pick_news(crypto_pool, "crypto", None, limit=3)
    if crypto_items:
        crypto_news_str = "\n".join(f"• {it.get('title', '')} ({it.get('source', '')})" for it in crypto_items)
    else:
        crypto_news_str = "• (tidak ada berita kripto relevan di feed saat ini)"

    # FIX: list only the sources actually quoted in this message (was: first 6 alphabetically).
    used = [it.get("source", "") for it in crypto_items]
    for v in md.values():
        n = (v or {}).get("news") or {}
        if n.get("available"):
            used.append(n.get("source", ""))
    sources_str = ", ".join(dict.fromkeys(s for s in used if s)) or "-"

    cal_block = ""
    if weekly_calendar:
        today_iso = wib_now.strftime("%Y-%m-%d")
        upcoming = [e for e in weekly_calendar if e.get("date_iso", "") >= today_iso]
        display_events = upcoming[:3] if upcoming else weekly_calendar[-3:]
        cal_items = []
        for e in display_events:
            d = e.get("date_iso", "")
            status_tag = "[HARI INI]" if d == today_iso else "[MENDATANG]" if d > today_iso else "[TELAH RILIS]"
            country = e.get("country", "US").replace("🇺🇸", "").replace("🇮🇩", "").strip()
            imp = e.get("importance", "TINGGI").replace("🔴", "").replace("🟡", "").replace("🟢", "").strip()
            item = (f"• {e.get('day', '')}, {e.get('date', '')} {e.get('time_wib', '')} {status_tag} "
                    f"[{country} {e.get('tz_tag', '')}]: {e.get('event', '')} [{imp}]")
            if status_tag == "[TELAH RILIS]":
                # FIX: a released event without its actual value is not usable.
                item += f"\n  - Aktual: {e['actual']}" if e.get("actual") else "\n  - Aktual: (belum tersedia di data)"
            item += f"\n  - Dampak Hot: {e.get('impact_hot', '-')}\n  - Aset Pilihan: {e.get('favored_asset', '-')}"
            cal_items.append(item)
        cal_block = ("\n━━━━━━━━━━━━━━━━━━━━━\nKATALIS KALENDER EKONOMI (FOKUS HARI INI & MENDATANG)\n"
                     + "\n".join(cal_items))

    indo_block = ""
    if indo_macro:
        # FIX: read every Indonesia number from indo_macro (one source). The old code re-read
        # prices with different defaults -> Rp 18,120 in one place and Rp 18,140 in another.
        lines = []
        if indo_macro.get("ihsg_val"):
            lines.append(f"• IHSG Spot: {indo_macro['ihsg_val']:,.2f} ({pct(indo_macro.get('ihsg_chg'))} 1D, "
                         f"{pct(indo_macro.get('ihsg_20d'), 1)} 20D) [{indo_macro.get('ihsg_status', '-')}]")
        if indo_macro.get("usdidr_val"):
            lines.append(f"• USD / IDR Spot: Rp {indo_macro['usdidr_val']:,.0f} "
                         f"({pct(indo_macro.get('usdidr_chg'))}) [{indo_macro.get('kurs_status', '-')}]")
        if indo_macro.get("eido_val"):
            lines.append(f"• MSCI Indonesia (EIDO): US$ {indo_macro['eido_val']:.2f} "
                         f"({pct(indo_macro.get('eido_chg'))}) [{indo_macro.get('eido_status', '-')}]")
        lines.append(f"• Kebijakan Bank Indonesia: {indo_macro.get('bi_status', '-')}")
        lines.append(f"• Analisis: {indo_macro.get('summary', '')}")
        indo_block = "\n━━━━━━━━━━━━━━━━━━━━━\nTRANSMISI KE PASAR MODAL INDONESIA\n" + "\n".join(lines)

    btc_20d = pct(btc["chg_20d"]) if btc else "n/a"
    msg = f"""Global Market Review
(Penutupan Wall Street: {session_str} | disusun {prepared_str})

{chain_section}

━━━━━━━━━━━━━━━━━━━━━
LIKUIDITAS THE FED (H.4.1 BALANCE SHEET)
• Likuiditas Bersih: US$ {nl_val:,.1f} Miliar
• Perubahan 4 Pekan: {nl_chg:+.1f} Miliar ({liq_label}{liq_pct})
• Komponen Neraca: Total Aset Fed (WALCL) - Saldo Depkeu (TGA) - Reverse Repo (RRP)
• Rilis berikutnya: {h41_release_text(wib_now)}

━━━━━━━━━━━━━━━━━━━━━
DINAMIKA PASAR KRIPTO
{_price_line("Bitcoin (BTC)", btc)} | 20D: {btc_20d}
{_price_line("Ethereum (ETH)", eth)}
{_price_line("Solana (SOL)", sol, "{:.2f}")}
• Status Altseason: {altseason_status}
• Berita Kripto & Web3:
{crypto_news_str}
{cal_block}
{indo_block}

━━━━━━━━━━━━━━━━━━━━━
SUMBER
• Data pasar: Yahoo Finance (yfinance); emas spot: FXRatesAPI; neraca & suku bunga: FRED (St. Louis Fed)
• Berita yang dikutip: {sources_str}

━━━━━━━━━━━━━━━━━━━━━
⚠️ Disclaimer: Ringkasan makroekonomi ini disusun untuk tujuan riset internal dan pemantauan pasar modal, bukan merupakan rekomendasi atau ajakan transaksi investasi.

Disusun oleh studikarangsambung-market pulse engine"""
    return msg.strip()


def generate_report_payload(snapshot, ews_signals, regime, corrs, sectors, crypto_data, eth_btc_ratio,
                            indo_macro=None, weekly_calendar=None, flow_proj=None, market_drivers=None):
    whatsapp_text = generate_whatsapp_broadcast(snapshot, ews_signals, regime, corrs, sectors, crypto_data,
                                                eth_btc_ratio, indo_macro, weekly_calendar, flow_proj,
                                                market_drivers)
    wib_now = get_wib_now()

    try:
        from ml4t_regime_engine import get_tri_asset_regimes
        ml4t_regimes = get_tri_asset_regimes(snapshot, snapshot.get("prices", {}), indo_macro)
    except Exception:
        ml4t_regimes = {}

    payload = {
        "ml4t_regimes": ml4t_regimes,
        "timestamp": wib_now.strftime("%Y-%m-%d %H:%M:%S"),
        "display_date": f"{wib_now.strftime('%A, %d %B %Y')} · {wib_now.strftime('%H:%M')} WIB",
        "iso_timestamp": wib_now.isoformat(),
        "regime": regime,
        "ews": ews_signals,
        "correlations": corrs,
        "sectors": sectors,
        "crypto": crypto_data,
        "eth_btc_ratio": eth_btc_ratio,
        "net_liquidity": snapshot.get("net_liquidity", {}),
        "macro_prices": snapshot.get("prices", {}),
        "news_by_category": snapshot.get("news_by_category", {}),
        "gold_news": snapshot.get("gold_news", []),
        "oil_news": snapshot.get("oil_news", []),
        "dollar_news": snapshot.get("dollar_news", []),
        "tech_news": snapshot.get("tech_news", []),
        "global_news": snapshot.get("global_news", []),
        "geopolitics_news": snapshot.get("geopolitics_news", []),
        "crypto_news": snapshot.get("crypto_news", []),
        "indonesia_news": snapshot.get("indonesia_news", []),
        "indo_macro": indo_macro,
        "weekly_calendar": weekly_calendar or [],
        "flow_proj": flow_proj or {},
        "market_drivers": market_drivers or {},
        "whatsapp_broadcast": whatsapp_text
    }
    return payload
