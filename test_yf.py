import yfinance as yf
import pandas as pd
import traceback
import requests

print("=== Network Connectivity Test ===")
try:
    response = requests.get("https://finance.yahoo.com", timeout=10)
    print(f"Yahoo Finance direct access: {response.status_code}")
except Exception as e:
    print(f"Yahoo Finance direct access failed: {e}")

print("\n=== Testing yfinance with Ticker.history ===")
try:
    ticker = yf.Ticker("AAPL")
    print("Ticker object created")
    hist = ticker.history(period="1mo", auto_adjust=True)
    print(f"History fetched. Shape: {hist.shape}")
    print(hist.tail())
    
    if hist.empty:
        print("History is EMPTY!")
    else:
        print("History OK - Data fetched successfully!")
        
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

print("\n=== Testing yfinance with yf.download ===")
try:
    data = yf.download("AAPL", period="1mo", progress=False, auto_adjust=True)
    print(f"Download fetched. Shape: {data.shape}")
    print(data.tail())
    
    if data.empty:
        print("Download data is EMPTY!")
    else:
        print("Download OK - Data fetched successfully!")
        
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

print("\n=== Testing with start/end dates ===")
try:
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = yf.download("AAPL", start=start_date, end=end_date, progress=False)
    print(f"Date-based download. Shape: {data.shape}")
    print(data.tail())
    
    if data.empty:
        print("Date-based download is EMPTY!")
    else:
        print("Date-based download OK!")
        
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
