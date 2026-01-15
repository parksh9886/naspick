
import yfinance as yf

try:
    print("Fetching MU...")
    ticker = yf.Ticker("MU")
    print(f"Info Mcap: {ticker.info.get('marketCap')}")
    print(f"Fast Info Mcap: {ticker.fast_info.get('market_cap')}")
except Exception as e:
    print(f"Error: {e}")
