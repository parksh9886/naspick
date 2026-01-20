import yfinance as yf
import pandas as pd

def check_earnings():
    ticker = "TSLA"
    print(f"Fetching earnings history for {ticker}...")
    t = yf.Ticker(ticker)
    
    try:
        # Check earnings_dates
        dates = t.earnings_dates
        print("\n--- earnings_dates ---")
        print(dates.head(5) if dates is not None else "None")
        
        # Check columns if it's a dataframe
        if isinstance(dates, pd.DataFrame):
            print("\nColumns:", dates.columns)
            
            # Try to get most recent past earnings
            # Filter for dates in the past
            now = pd.Timestamp.now().tz_localize(dates.index.dtype.tz)
            past = dates[dates.index < now]
            if not past.empty:
                print("\nMost recent past earnings:")
                print(past.iloc[0])
            
    except Exception as e:
        print(f"Error fetching earnings_dates: {e}")

    try:
        # Check quarterly_earnings
        q = t.quarterly_earnings
        print("\n--- quarterly_earnings ---")
        print(q)
    except Exception as e:
        print(f"Error fetching quarterly_earnings: {e}")

if __name__ == "__main__":
    check_earnings()
