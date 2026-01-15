import yfinance as yf
import json

def check_yfinance(ticker):
    print(f"Fetching {ticker}...")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract relevant fields
        data = {
            "symbol": ticker,
            "currentPrice": info.get('currentPrice'),
            "targetHighPrice": info.get('targetHighPrice'),
            "targetLowPrice": info.get('targetLowPrice'),
            "targetMeanPrice": info.get('targetMeanPrice'),
            "recommendationMean": info.get('recommendationMean'),
            "recommendationKey": info.get('recommendationKey')
        }
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_yfinance("AAPL")
    check_yfinance("NVDA")
