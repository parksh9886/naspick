
import yfinance as yf
import pandas as pd
from datetime import datetime

def debug_ticker(symbol):
    print(f"--- Debugging {symbol} ---")
    ticker = yf.Ticker(symbol)
    
    print("[1] ticker.calendar:")
    try:
        cal = ticker.calendar
        print(cal)
    except Exception as e:
        print(f"Error accessing calendar: {e}")

    print("\n[2] ticker.earnings_dates (Head 5):")
    try:
        ed = ticker.earnings_dates
        if ed is not None and not ed.empty:
            print(ed.head(5))
            
            # Try to find next earnings
            now = pd.Timestamp.now().tz_localize(ed.index.dtype.tz)
            future = ed[ed.index >= now]
            if not future.empty:
                print(f"Found future earnings in earnings_dates: {future.index[-1]} (furthest) ... {future.index[0]} (nearest)")
                # earnings_dates index is usually sorted descending? No, let's check.
                # Usually it is sorted descending by date. 
                # So the "nearest future" would be the last element of the 'future' dataframe if it's descending?
                # Actually let's assume nothing and sort.
                future_sorted = future.sort_index()
                print(f"Nearest Future Earnings: {future_sorted.index[0]}")
            else:
                print("No future earnings found in earnings_dates.")
        else:
            print("earnings_dates is empty.")
    except Exception as e:
        print(f"Error accessing earnings_dates: {e}")

    print("\n[3] ticker.dividends (Tail 5):")
    try:
        divs = ticker.dividends
        if not divs.empty:
            print(divs.tail(5))
        else:
            print("No dividends found.")
    except Exception as e:
        print(f"Error accessing dividends: {e}")

if __name__ == "__main__":
    debug_ticker("UHS")
    debug_ticker("AAPL")
