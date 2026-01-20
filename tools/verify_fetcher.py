
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core.fetcher import StockDataFetcher

def verify_fetcher():
    print("--- Verifying StockDataFetcher.fetch_calendar_data_bulk ---")
    fetcher = StockDataFetcher()
    tickers = ['UHS', 'AAPL', 'TSLA']
    
    data = fetcher.fetch_calendar_data_bulk(tickers)
    
    print(json.dumps(data, indent=4))
    
    # Check checks
    for t in tickers:
        if t in data:
            print(f"[{t}] Next Earnings: {data[t].get('next_earnings', 'N/A')}")
            print(f"[{t}] Ex-Div: {data[t].get('ex_dividend_date', 'N/A')}")
        else:
            print(f"[{t}] No data found.")

if __name__ == "__main__":
    verify_fetcher()
