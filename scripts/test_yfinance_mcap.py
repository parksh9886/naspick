import yfinance as yf

tickers = ["AAPL", "GOOGL", "TSLA", "BRK-B"]
print(f"Testing market cap fetch for: {tickers}")

try:
    # Method 1: yf.Tickers (Batch) -> This is usually faster but sometimes misses info
    print("\n--- Method 1: Batch Fetch ---")
    batch = yf.Tickers(" ".join(tickers))
    for t, ticker_obj in batch.tickers.items():
        try:
            info = ticker_obj.info
            mcap = info.get('marketCap', 0)
            print(f"{t}: {mcap:,}")
        except Exception as e:
            print(f"{t}: Error {e}")

    # Method 2: Individual Fetch (Fallback)
    # Sometimes batch info is incomplete
except Exception as e:
    print(f"Global Error: {e}")
