
import yfinance as yf
import pandas as pd

def compare():
    symbol = "UHS"
    print(f"--- Comparing {symbol} ---")
    
    # Method 1: Single Ticker
    t1 = yf.Ticker(symbol)
    ed1 = t1.earnings_dates
    print(f"[Single] earnings_dates head:\n{ed1.head(3) if ed1 is not None else 'None'}")
    
    # Method 2: Batch Tickers
    ts = yf.Tickers(symbol)
    t2 = ts.tickers[symbol]
    ed2 = t2.earnings_dates
    print(f"[Batch] earnings_dates head:\n{ed2.head(3) if ed2 is not None else 'None'}")

    symbol = "AAPL"
    print(f"\n--- Comparing {symbol} ---")
    t1 = yf.Ticker(symbol)
    ed1 = t1.earnings_dates
    print(f"[Single] earnings_dates head:\n{ed1.head(3) if ed1 is not None else 'None'}")
    
    ts = yf.Tickers(symbol)
    t2 = ts.tickers[symbol]
    ed2 = t2.earnings_dates
    print(f"[Batch] earnings_dates head:\n{ed2.head(3) if ed2 is not None else 'None'}")

if __name__ == "__main__":
    compare()
