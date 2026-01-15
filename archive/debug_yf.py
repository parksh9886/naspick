import yfinance as yf

def test_yf():
    print("Testing yfinance single ticker...")
    t = yf.Ticker("AAPL")
    print(f"AAPL Market Cap: {t.info.get('marketCap')}")
    
    print("\nTesting yfinance batch...")
    tickers = yf.Tickers("AAPL MSFT")
    # New yfinance Access pattern might be tickers.tickers['AAPL'].info
    print(f"Keys: {tickers.tickers.keys()}")
    try:
        print(f"AAPL Batch Market Cap: {tickers.tickers['AAPL'].info.get('marketCap')}")
    except Exception as e:
        print(f"Error accessing batch info: {e}")

if __name__ == "__main__":
    test_yf()
