import requests
import json
from datetime import datetime, timedelta
import time

# Test direct Yahoo Finance chart API
print("=== Testing Direct Yahoo Finance API ===")

# This is the endpoint yfinance typically uses
url = "https://query2.finance.yahoo.com/v8/finance/chart/AAPL"

params = {
    'interval': '1d',
    'range': '1mo'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response length: {len(response.text)} bytes")
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== Response Structure ===")
        print(f"Keys: {list(data.keys())}")
        
        if 'chart' in data:
            chart = data['chart']
            print(f"Chart keys: {list(chart.keys())}")
            
            if 'result' in chart and chart['result']:
                result = chart['result'][0]
                print(f"Result keys: {list(result.keys())}")
                
                if 'timestamp' in result and result['timestamp']:
                    print(f"\nNumber of data points: {len(result['timestamp'])}")
                    print(f"First timestamp: {datetime.fromtimestamp(result['timestamp'][0])}")
                    print(f"Last timestamp: {datetime.fromtimestamp(result['timestamp'][-1])}")
                    
                    if 'indicators' in result and 'quote' in result['indicators']:
                        quote = result['indicators']['quote'][0]
                        print(f"Quote keys: {list(quote.keys())}")
                        print(f"Close prices (last 5): {quote['close'][-5:]}")
                        print("\n✓ SUCCESS! API returns valid data!")
                else:
                    print("ERROR: No timestamp data in result")
            else:
                print("ERROR: No result in chart response")
                if 'error' in chart:
                    print(f"API Error: {chart['error']}")
        else:
            print("ERROR: No chart in response")
            print(f"Full response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"ERROR: Bad status code")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Testing yfinance after confirming API works ===")
import yfinance as yf
ticker = yf.Ticker("AAPL")
print(f"yfinance version: {yf.__version__}")

# Enable debugging
import logging
logging.basicConfig(level=logging.DEBUG)

hist = ticker.history(period="5d")
print(f"yfinance result shape: {hist.shape}")
print(hist)
