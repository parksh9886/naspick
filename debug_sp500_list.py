
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.core.fetcher import StockDataFetcher

def check():
    print("Initializing Fetcher...")
    f = StockDataFetcher()
    
    print("Fetching S&P 500 Ticker List...")
    tickers = f.get_sp500_tickers()
    
    print(f"✅ Total Tickers Fetched: {len(tickers)}")
    
    # Check key tickers
    check_list = ['BRK.B', 'BRK-B', 'BF.B', 'BF-B', 'O', 'AAPL']
    for t in check_list:
        print(f" - {t}: {'FOUND' if t in tickers else 'MISSING'}")

if __name__ == "__main__":
    check()
