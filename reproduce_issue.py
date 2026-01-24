import sys
import os
import yfinance as yf

# Ensure scripts directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scripts.core.consensus import ConsensusManager
    from scripts.core.fetcher import StockDataFetcher
    
    print("✅ Imports successful.")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_single_fetch():
    print("🚀 Testing single stock fetch...")
    manager = ConsensusManager()
    
    # Mock data fetcher to return just one ticker
    # Or just use the manager logic manually for one ticker
    ticker = "AAPL"
    yf_ticker = "AAPL"
    
    print(f"Fetching {ticker}...")
    try:
        stock = yf.Ticker(yf_ticker)
        info = stock.info
        print(f"✅ Info fetched. Keys: {list(info.keys())[:5]}...")
        
        rec_mean = info.get('recommendationMean')
        print(f"Recommendation Mean: {rec_mean}")
        
    except Exception as e:
        print(f"❌ Error fetching {ticker}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_fetch()
