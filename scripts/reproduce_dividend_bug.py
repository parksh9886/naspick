
import yfinance as yf
import pandas as pd

def test_dividend_yield():
    ticker = "EIX"
    print(f"Testing dividend yield for {ticker}...")
    
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info
    
    if info and 'dividendYield' in info:
        raw_yield = info['dividendYield']
        print(f"Raw dividendYield from yfinance: {raw_yield}")
        
        # Current Logic causing bug
        calculated = round(raw_yield * 100, 2)
        print(f"Current Logic (yield * 100): {calculated}")
        
        # Expected fix
        if raw_yield > 0.5: # Likely already percent if > 0.5 (50%)
             print(f"Proposed Fix Logic: {round(raw_yield, 2)}")
        else:
             print(f"Proposed Fix Logic: {round(raw_yield * 100, 2)}")
    else:
        print("dividendYield not found in info")

if __name__ == "__main__":
    test_dividend_yield()
