import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core.fetcher import StockDataFetcher
from scripts.config import PATHS

def update_calendar_data():
    print(f"📅 Starting Daily Calendar Update: {datetime.now()}")
    
    fetcher = StockDataFetcher()
    
    # 1. Get Tickers (S&P 500)
    print("   Getting S&P 500 tickers...")
    tickers = fetcher.get_sp500_tickers()
    
    # 2. Fetch Calendar Data (Earnings, Dividends, etc.)
    print(f"   Fetching calendar data for {len(tickers)} tickers...")
    calendar_data = fetcher.fetch_calendar_data_bulk(tickers)
    
    # 3. Save to JSON
    output_path = os.path.join("data", "calendar_data.json")
    
    # Load existing to preserve if fetch fails partly? 
    # Actually fetch_calendar_data_bulk returns all or nothing for the batch usually.
    # We will overwrite to keep it fresh.
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(calendar_data, f, indent=4)
        
    print(f"✅ Calendar data saved to {output_path} ({len(calendar_data)} items)")

if __name__ == "__main__":
    update_calendar_data()
