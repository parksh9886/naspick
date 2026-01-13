
import yfinance as yf
import time

tickers = ["AAPL", "NVDA", "BRK-B", "TSLA", "MSFT"]

print("🚀 Testing yfinance Market Cap fetching...")

print("\n--- Method 1: yf.Ticker(t).fast_info ---")
start = time.time()
for t in tickers:
    try:
        ticker = yf.Ticker(t)
        mcap = ticker.fast_info.get('market_cap')
        print(f"  {t}: {mcap}")
    except Exception as e:
        print(f"  {t}: ❌ Error: {e}")
print(f"⏱ Time: {time.time() - start:.2f}s")

print("\n--- Method 2: yf.Ticker(t).info ---")
start = time.time()
for t in tickers:
    try:
        ticker = yf.Ticker(t)
        # accessing .info forces a scrape usually
        info = ticker.info
        mcap = info.get('marketCap')
        print(f"  {t}: {mcap}")
    except Exception as e:
        print(f"  {t}: ❌ Error: {e}")
print(f"⏱ Time: {time.time() - start:.2f}s")
