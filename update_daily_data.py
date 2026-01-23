import sys
import os
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.core.consensus import ConsensusManager
from scripts.core.fetcher import StockDataFetcher
import json

def run_daily_update():
    """
    Unified entry point for Daily Heavy Tasks (Consensus + Calendar).
    Runs once a day (e.g. 09:00 UTC) via Github Actions.
    """
    print(f"🚀 [Daily Update] Started at {datetime.now()}")
    
    # 1. Consensus Update (Targets, Recommendations, Financial Health)
    print("\n" + "="*50)
    print("📡 STEP 1: Fetching Wall St. Consensus & Financials")
    print("="*50)
    try:
        consensus_mgr = ConsensusManager()
        consensus_mgr.fetch_all_consensus()
        print("✅ Consensus Update Completed.")
    except Exception as e:
        print(f"❌ Consensus Update Failed: {e}")

    # 2. Calendar Update (Earnings, Dividends)
    print("\n" + "="*50)
    print("📅 STEP 2: Fetching Calendar Data (Earnings & Dividends)")
    print("="*50)
    try:
        fetcher = StockDataFetcher()
        tickers = fetcher.get_sp500_tickers()
        print(f"   Fetching calendar data for {len(tickers)} tickers...")
        
        calendar_data = fetcher.fetch_calendar_data_bulk(tickers)
        
        output_path = os.path.join("data", "calendar_data.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(calendar_data, f, indent=4)
            
        print(f"✅ Calendar Data saved to {output_path} ({len(calendar_data)} items)")
        
    except Exception as e:
        print(f"❌ Calendar Update Failed: {e}")

    # 3. Financials Update (New)
    print("\n" + "="*50)
    print("💰 STEP 3: Updating Financial Data (Smart Mode)")
    print("="*50)
    try:
        # Import inside function to avoid circular imports or early failure
        from scripts.mining.fetch_financials import update_financials
        update_financials(mode='smart')
    except Exception as e:
        print(f"❌ Financials Update Failed: {e}")

    print(f"\n✨ [Daily Update] All tasks finished at {datetime.now()}")

if __name__ == "__main__":
    run_daily_update()
