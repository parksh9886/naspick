import fetch_sp500 as fdr_script
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

def test_briefing(ticker="DAY"):
    print(f"🧪 Testing Data Fetch for {ticker}...")
    
    # Mock data fetch
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    try:
        hist = fdr.DataReader(ticker, start_date, end_date)
        if hist.empty:
            print("No history found.")
            return

        result = fdr_script.calculate_naspick_score(ticker, hist)
        if not result:
            print("Calculation failed.")
            return

        print(f"\nTick: {result['ticker']}")
        print(f"Exchange: {result.get('exchange', 'N/A')}")
        print(f"Sector: {result['sector']}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_briefing()
