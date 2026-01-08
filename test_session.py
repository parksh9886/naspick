import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta

# Custom session with headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

print("=== Testing with Custom Session ===")
try:
    ticker = yf.Ticker("AAPL", session=session)
    hist = ticker.history(period="1mo")
    print(f"History shape: {hist.shape}")
    print(hist.tail())
    
    if not hist.empty:
        print("SUCCESS! Data fetched with custom session!")
    else:
        print("Still empty with custom session")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Trying different ticker ===")
try:
    ticker2 = yf.Ticker("MSFT", session=session)
    hist2 = ticker2.history(period="5d")
    print(f"MSFT History shape: {hist2.shape}")
    print(hist2.tail())
    
    if not hist2.empty:
        print("SUCCESS with MSFT!")
    else:
        print("MSFT also empty")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
