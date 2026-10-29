"""
Background Auto-Updater Scheduler for Macro Pulse Engine
Runs main.py on a regular interval or specific market hours.
"""

import time
import datetime
import sys
from main import run_pipeline

INTERVAL_MINUTES = 60  # Update every 60 minutes

def start_scheduler():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=" * 60)
    print("⏱️ MACRO PULSE AUTO-SCHEDULER ACTIVATED")
    print(f"🔄 Interval: Every {INTERVAL_MINUTES} minutes")
    print("=" * 60)
    
    while True:
        try:
            print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Triggering scheduled macro update...")
            run_pipeline(sync=True, print_wa=False)
            print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Update complete. Next run in {INTERVAL_MINUTES} minutes.")
        except Exception as e:
            print(f"Error during auto-update: {e}")
            
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    start_scheduler()
