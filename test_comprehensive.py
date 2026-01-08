import yfinance as yf
from datetime import datetime, timedelta

print(f"yfinance version: {yf.__version__}")
print("\n=== Basic Test ===")

try:
    # Try with very simple parameters
    ticker = yf.Ticker("AAPL")
    
    # Try different period formats
    print("\nTest 1: period='1mo'")
    hist1 = ticker.history(period="1mo")
    print(f"Shape: {hist1.shape}, Empty: {hist1.empty}")
    if not hist1.empty:
        print(hist1.tail(3))
    
    print("\nTest 2: period='5d'")
    hist2 = ticker.history(period="5d")
    print(f"Shape: {hist2.shape}, Empty: {hist2.empty}")
    if not hist2.empty:
        print(hist2.tail(3))
    
    print("\nTest 3: Using start/end dates")
    end = datetime.now()
    start = end - timedelta(days=7)
    hist3 = ticker.history(start=start, end=end)
    print(f"Shape: {hist3.shape}, Empty: {hist3.empty}")
    if not hist3.empty:
        print(hist3.tail(3))
        
    print("\nTest 4: yf.download")
    data = yf.download("AAPL", period="5d", progress=False)
    print(f"Shape: {data.shape}, Empty: {data.empty}")
    if not data.empty:
        print(data.tail(3))
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== If all tests show empty, there's a yfinance bug with this Python version ===")
