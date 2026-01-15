import json
import yfinance as yf

def check():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("data.json not found")
        return

    # Find DAY
    day_item = next((d for d in data if d['ticker'] == 'DAY'), None)
    if day_item:
        print(f"Stored Ticker: {day_item['ticker']}")
        print(f"Stored Name: {day_item.get('name')}")
        print(f"Stored Price: {day_item.get('current_price')}")
        print(f"Stored Date: {day_item.get('last_updated', 'Unknown')}")
    else:
        print("DAY not found in data.json")

    # Check Real Price
    print("\nFetching real price for DAY...")
    try:
        t = yf.Ticker("DAY")
        # Try fast_info
        price = t.fast_info.get('last_price')
        print(f"Real Price (YF fast_info): {price}")
        
        # Try history
        hist = t.history(period='1d')
        if not hist.empty:
            print(f"Real Price (YF History Close): {hist['Close'].iloc[-1]}")
            
    except Exception as e:
        print(f"Error fetching YF: {e}")

if __name__ == "__main__":
    check()
