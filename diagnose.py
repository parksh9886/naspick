import requests

print("=== Simple Yahoo Finance API Test ===\n")

url = "https://query2.finance.yahoo.com/v8/finance/chart/AAPL"
params = {'interval': '1d', 'range': '5d'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 429:
        print("\n❌ CONFIRMED: HTTP 429 - Too Many Requests")
        print("Yahoo Finance is rate-limiting this IP address.")
        print("\nPossible reasons:")
        print("1. Too many requests from this IP/environment") 
        print("2. Yahoo's anti-bot protection")
        print("3. Geographic or datacenter IP blocking")
        print("\nSolution: yfinance cannot work from this environment.")
        print("You'll need to run scorer.py from your local machine or a different network.")
    elif response.status_code == 200:
        print("\n✓ SUCCESS: API accessible!")
        data = response.json()
        timestamps = data.get('chart', {}).get('result', [{}])[0].get('timestamp', [])
        print(f"Data points received: {len(timestamps)}")
    else:
        print(f"\nUnexpected status code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"Error: {e}")
