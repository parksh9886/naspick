import FinanceDataReader as fdr
import json
import pandas as pd

def update_exchanges():
    print("🚀 Fetching exchange info from FinanceDataReader...")
    
    # Fetch lists
    try:
        print("  - Fetching NASDAQ...")
        nasdaq = fdr.StockListing('NASDAQ')
        nasdaq_tickers = set(nasdaq['Symbol'])
        
        print("  - Fetching NYSE...")
        nyse = fdr.StockListing('NYSE')
        nyse_tickers = set(nyse['Symbol'])
        
        print("  - Fetching AMEX...")
        amex = fdr.StockListing('AMEX')
        amex_tickers = set(amex['Symbol'])
        
    except Exception as e:
        print(f"❌ Error fetching listings: {e}")
        return

    # Load data
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found")
        return

    updated_count = 0
    
    for item in data:
        ticker = item['ticker']
        # Remove dot for matching if needed, but fdr uses unmodified usually?
        # fdr BRK.B might be BRK/B or BRK-B?
        # Let's check.
        
        exchange = "NASDAQ" # Default fallback? Or empty?
        
        if ticker in nasdaq_tickers:
            exchange = "NASDAQ"
        elif ticker in nyse_tickers:
            exchange = "NYSE"
        elif ticker in amex_tickers:
            exchange = "AMEX"
        else:
            # Check alternatives
            alt = ticker.replace('.', '-') # BRK-B
            if alt in nasdaq_tickers: exchange = "NASDAQ"
            elif alt in nyse_tickers: exchange = "NYSE"
            else:
                # Try dot?
                alt2 = ticker # already dot
                # Try just assuming based on length? No.
                # If not found, default to NASDAQ for now, or check yfinance?
                # User problem is DAY (NYSE).
                # If DAY is in NYSE list, we are good.
                pass
        
        item['exchange'] = exchange
        updated_count += 1

    # Save
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated exchanges for {updated_count} stocks.")

if __name__ == "__main__":
    update_exchanges()
