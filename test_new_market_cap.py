
import FinanceDataReader as fdr
import pandas as pd

def get_market_caps_bulk_test(tickers):
    print(f"💰 Fetching Market Caps for {len(tickers)} tickers via FinanceDataReader...")
    mcaps = {}
    
    try:

        # Fetch SP500 data
        print("  - Fetching SP500...")
        df_sp500 = fdr.StockListing('SP500')
        print(f"    SP500 rows: {len(df_sp500)}")
        print(f"    SP500 Columns: {df_sp500.columns.tolist()}")

        combined = df_sp500
        print(f"  Total combined rows: {len(combined)}")
        print(f"  Columns: {combined.columns.tolist()}")
        
        # Create lookup
        col = 'MarCap' if 'MarCap' in combined.columns else 'MarketCap'
        print(f"  - Using column: {col}")
        
        if col in combined.columns:
            mc_lookup = dict(zip(combined['Symbol'], combined[col]))
            
            # DEBUG: Print some keys
            print(f"  Sample keys in lookup: {list(mc_lookup.keys())[:10]}")
            if "AAPL" in mc_lookup: print("  AAPL is in lookup!")
            else: print("  AAPL is NOT in lookup!")
            
            for t in tickers:
                mc = mc_lookup.get(t)
                if not mc:
                    # Try hyphenated for lookup
                    mc = mc_lookup.get(t.replace('.', '-'))
                
                if mc:
                    mcaps[t] = int(mc)
                else:
                    mcaps[t] = 0
                    print(f"  Failed for {t}")
    except Exception as e:
        print(f"❌ Error fetching market cap data: {e}")
        return {}
            
    print(f"✓ Market Cap fetch complete. Found {len(mcaps)}/{len(tickers)}")
    return mcaps

if __name__ == "__main__":
    tickers = ["AAPL", "BRK.B", "NVDA", "KVUE"] # Test a mix: Standard, Dot, Newish
    mcaps = get_market_caps_bulk_test(tickers)
    print("Results:")
    for t, m in mcaps.items():
        print(f"  {t}: {m}")
