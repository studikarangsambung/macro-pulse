"""
Automated 5-Minute Live Market Sync & Git Deploy Daemon
Natural Horizon · studikarangsambung-market pulse engine

Runs every 5 minutes:
1. Ingests real-time live prices (Gold Spot XAUUSD, BTC, ETH, SOL, WTI, S&P 500, Yields) & fresh sentiment.
2. Recalculates quantitative models, regime probabilities, and dynamic narratives.
3. Compiles terminal HTML reports (index.html & report_us_macro.html).
4. Commits and pushes updates to GitHub repository automatically.
"""

import time
import datetime
import subprocess
import sys
import os

INTERVAL_SECONDS = 300  # 5 minutes

def run_sync_cycle(cycle_num):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n============================================================")
    print(f"🔄 [CYCLE #{cycle_num}] {now_str} - STARTING 5-MIN LIVE SYNC")
    print(f"============================================================")
    
    # 1. Execute Pipeline
    try:
        t0 = time.time()
        res = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True, check=True)
        dur = round(time.time() - t0, 1)
        print(f"✅ Pipeline executed successfully in {dur}s.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Pipeline failed: {e}")
        print(e.stderr)
        return False

    # 2. Git Status Check & Push
    try:
        subprocess.run(["git", "add", "index.html", "report_us_macro.html", "data/"], check=True)
        # Check if changes exist
        diff_check = subprocess.run(["git", "diff", "--staged", "--quiet"])
        if diff_check.returncode != 0:
            commit_msg = f"chore(auto): 5-min live sync {now_str} [skip ci]"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            push_res = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            if push_res.returncode == 0:
                print(f"🚀 Changes successfully pushed to GitHub & deployed live.")
            else:
                print(f"⚠️ Git push notice: {push_res.stderr.strip() or push_res.stdout.strip()}")
        else:
            print("ℹ️ No data diff detected in this cycle (market values stable).")
    except Exception as ge:
        print(f"⚠️ Git synchronization exception: {ge}")

    return True

def main():
    print("============================================================")
    print("⚡ MACRO PULSE 5-MINUTE AUTO-SYNC DAEMON INITIALIZED")
    print(f"⏰ Frequency: Every {INTERVAL_SECONDS // 60} minutes ({INTERVAL_SECONDS}s)")
    print("🌐 Target: Live Market Data + GitHub Pages Terminal")
    print("Press Ctrl+C to stop the daemon at any time.")
    print("============================================================")
    
    cycle = 1
    while True:
        try:
            run_sync_cycle(cycle)
            cycle += 1
            print(f"\n⏳ Sleeping for {INTERVAL_SECONDS // 60} minutes until next cycle...")
            time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\n🛑 Daemon stopped by user. Exiting cleanly.")
            break
        except Exception as ex:
            print(f"⚠️ Unexpected error in main loop: {ex}")
            time.sleep(30)

if __name__ == "__main__":
    main()
