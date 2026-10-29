"""
Master Orchestrator for US Macro & Crypto Pulse Engine
Runs Ingestion, Quantitative Analytics, Economic Calendar, Flow Projections, WhatsApp Chain, and Retro Classic Terminal HTML Report.
"""

import sys
import argparse
sys.stdout.reconfigure(encoding='utf-8')
from data_fetcher import init_db, sync_fred_data, compute_net_liquidity, sync_market_data, sync_news_data, get_latest_snapshot
from analytics_engine import evaluate_ews, classify_macro_regime, compute_correlation_matrix, compute_sector_scorecard, compute_crypto_scorecard, load_price_history, analyze_indonesia_macro_sentiment
from calendar_engine import get_weekly_economic_calendar, compute_macro_flow_projections
from narrative_generator import generate_report_payload, generate_whatsapp_broadcast
from html_generator import render_html_report

def run_pipeline(sync=True, print_wa=True):
    print("=" * 60)
    print("🚀 LAUNCHING MACRO PULSE · US SECTORS & CRYPTO ENGINE")
    print("=" * 60)
    
    init_db()
    
    if sync:
        print("\n[1/5] Ingesting point-in-time FRED balance sheet & indicators...")
        sync_fred_data()
        print("      Calculating Fed Net Liquidity...")
        compute_net_liquidity()
        print("      Ingesting 26 market tickers (US Sectors, Yields, Gold, USD/IDR, Crypto)...")
        sync_market_data(days=90)
        print("      Ingesting verified Global & Indonesia Macro News RSS...")
        sync_news_data()
    else:
        print("\n[1/5] Skipping live sync, reading cached database...")
        
    print("\n[2/5] Running Quantitative Analytics & Regime Classifier...")
    snapshot = get_latest_snapshot()
    price_df = load_price_history()
    
    ews = evaluate_ews(snapshot)
    regime = classify_macro_regime(snapshot, ews)
    corrs = compute_correlation_matrix(price_df)
    sectors = compute_sector_scorecard(snapshot, regime)
    crypto_data, eth_btc = compute_crypto_scorecard(snapshot)
    indo_macro = analyze_indonesia_macro_sentiment(snapshot, ews, regime)
    
    print(f"      Regime: {regime['title']}")
    print(f"      EWS: {regime['score_bahaya']} Bahaya, {regime['score_waspada']} Waspada")
    print(f"      Top Sector Pick: {sectors[0]['ticker']} ({sectors[0]['name']})")
    print(f"      USD/IDR: Rp {indo_macro['usdidr_val']:,.0f} [{indo_macro['kurs_status']}]")
    print(f"      Crypto Stance: {regime['crypto_stance']}")
    
    print("\n[3/5] Executing Phase 3: Weekly Economic Calendar & Flow Projections...")
    weekly_cal = get_weekly_economic_calendar()
    flow_proj = compute_macro_flow_projections(snapshot, regime, ews)
    print(f"      Weekly Calendar Events: {len(weekly_cal)} high-impact releases")
    print(f"      Liquidity Flow Regime: {flow_proj.get('primary_flow_regime', 'ROTASI SIKLIKAL')}")
    
    print("\n[4/5] Synthesizing Causality Chain & WhatsApp Broadcast...")
    payload = generate_report_payload(snapshot, ews, regime, corrs, sectors, crypto_data, eth_btc, indo_macro, weekly_cal, flow_proj)
    
    print("\n[5/5] Generating Natural Horizon Terminal HTML Report...")
    report_file = render_html_report(payload, output_path="report_us_macro.html")
    print(f"      Dashboard generated: file:///{report_file.replace('\\', '/')}")
    
    if print_wa:
        print("\n" + "=" * 60)
        print("📲 WHATSAPP BROADCAST (READY TO COPY):")
        print("=" * 60)
        # Safe print for console encodings
        sys.stdout.reconfigure(encoding='utf-8')
        print(payload["whatsapp_broadcast"])
        print("=" * 60)
        
    print("\n✅ PIPELINE COMPLETED SUCCESSFULLY.")
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run US Macro & Crypto Pulse Engine")
    parser.add_argument("--no-sync", action="store_true", help="Skip live sync and use cached db")
    parser.add_argument("--no-wa", action="store_true", help="Don't print WhatsApp text to console")
    args = parser.parse_args()
    
    run_pipeline(sync=not args.no_sync, print_wa=not args.no_wa)
