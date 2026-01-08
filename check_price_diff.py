import json
import yfinance as yf

def check_prices():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading data.json: {e}")
        return

    # Tickers to check: DAY (user report), AAPL, MSFT (reference)
    check_list = ['DAY', 'AAPL', 'MSFT', 'TSLA']
    
    print(f"{'Ticker':<8} | {'Stored Price':<12} | {'Real Price (YF)':<15} | {'Diff %':<10}")
    print("-" * 55)

    for ticker in check_list:
        # Find in data.json
        stored_item = next((item for item in data if item['ticker'] == ticker), None)
        stored_price = stored_item['current_price'] if stored_item else None
        
        # Get real price
        try:
            # Handle dot notation for YF
            yf_ticker = ticker.replace('.', '-')
            t = yf.Ticker(yf_ticker)
            # Try fast_info first (last_price)
            real_price = t.fast_info.get('last_price')
            if not real_price:
                 # Fallback to history
                 hist = t.history(period="1d")
                 if not hist.empty:
                     real_price = hist['Close'].iloc[-1]
        except Exception as e:
            real_price = f"Error: {e}"

        percent_diff = "N/A"
        if stored_price and isinstance(real_price, (int, float)):
             diff = abs(stored_price - real_price)
             percent_diff = f"{(diff / real_price) * 100:.2f}%"

        print(f"{ticker:<8} | {str(stored_price):<12} | {str(real_price):<15} | {percent_diff:<10}")

if __name__ == "__main__":
    check_prices()
