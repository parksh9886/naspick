import FinanceDataReader as fdr
import json
import pandas as pd

def update_market_caps():
    print("🚀 Fetching market cap data from FinanceDataReader...")
    
    # Fetch broad US market data which contains Market Cap
    try:
        print("  - Fetching NASDAQ...")
        df_nasdaq = fdr.StockListing('NASDAQ')
        print("  - Fetching NYSE...")
        df_nyse = fdr.StockListing('NYSE')
        print("  - Fetching AMEX...")
        df_amex = fdr.StockListing('AMEX')
        
        # Combine
        combined = pd.concat([df_nasdaq, df_nyse, df_amex])
        
        # Create a dictionary: Symbol -> MarketCap (Note: key might be 'MarCap' or 'MarketCap')
        # Check columns
        col = 'MarCap' if 'MarCap' in combined.columns else 'MarketCap'
        if col not in combined.columns:
             print(f"⚠ Columns found: {combined.columns}")
             return

        mc_lookup = dict(zip(combined['Symbol'], combined[col]))
        
    except Exception as e:
        print(f"❌ Error fetching market cap data: {e}")
        return

    print(f"✓ Loaded market cap data for {len(mc_lookup)} tickers")

    # Load existing data.json
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found")
        return

    updated_count = 0
    
    print("\nProcessing updates...")
    
    for item in data:
        ticker = item['ticker']
        
        # Lookup
        mc = mc_lookup.get(ticker)
        if not mc:
            mc = mc_lookup.get(ticker.replace('.', '-'))
            
        if mc:
            item['market_cap'] = int(mc)
            updated_count += 1
        else:
            # If not found, leave as 0 or try to infer? 
            # For now, just warn.
            pass
            # print(f"⚠ No market cap data found for {ticker}")

    # Save details
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated market caps for {updated_count} stocks.")

if __name__ == "__main__":
    update_market_caps()
