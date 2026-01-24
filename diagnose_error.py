import sys
import os
import yfinance as yf
import traceback
import json

# Ensure scripts directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.core.fetcher import StockDataFetcher
from scripts.config import PATHS

def diagnose():
    print("🏥 Starting Diagnostic Check...")
    
    # 1. Check Paths
    print("\n[1/4] Checking Paths...")
    output_dir = os.path.dirname(PATHS['CONSENSUS_JSON'])
    if not os.path.exists(output_dir):
        print(f"❌ Output directory does not exist: {output_dir}")
        try:
            os.makedirs(output_dir)
            print(f"✅ Created output directory: {output_dir}")
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return
    else:
        print(f"✅ Output directory exists: {output_dir}")
        
    # Check write permission
    try:
        test_file = os.path.join(output_dir, "test_write.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("✅ Write permission confirmed.")
    except Exception as e:
        print(f"❌ Write permission denied: {e}")
        return

    # 2. Check Ticker Fetching
    print("\n[2/4] Checking Ticker Source...")
    try:
        fetcher = StockDataFetcher()
        tickers = fetcher.get_sp500_tickers()
        print(f"✅ Fetched {len(tickers)} tickers.")
        if not tickers:
            print("❌ Ticker list is empty!")
            return
    except Exception as e:
        print(f"❌ Failed to fetch tickers: {e}")
        traceback.print_exc()
        return

    # 3. Test Consensus Fetch (Batch of 5)
    print("\n[3/4] Testing Consensus Fetch (First 5 tickers)...")
    success_count = 0
    
    test_tickers = tickers[:5]
    for ticker in test_tickers:
        print(f"   Fetching {ticker}...", end='')
        try:
            yf_ticker = ticker.replace('.', '-')
            stock = yf.Ticker(yf_ticker)
            info = stock.info
            
            # Check a key field
            rm = info.get('recommendationMean')
            print(f" ✅ Success (RecMean: {rm})")
            success_count += 1
            
        except Exception as e:
            print(f" ❌ Failed: {e}")
            traceback.print_exc()
            
    if success_count == 0:
        print("❌ All 5 fetches failed. Likely network/library issue.")
    elif success_count < 5:
        print("⚠️ Some fetches failed.")
    else:
        print("✅ Batch fetch successful.")

    print("\n🏥 Diagnostic Complete.")

if __name__ == "__main__":
    diagnose()
