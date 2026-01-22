
import pandas as pd
import os

CSV_PATH = os.path.join("data", "financials.csv")

def patch_financials():
    if not os.path.exists(CSV_PATH):
        print(f"❌ File not found: {CSV_PATH}")
        return

    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # Check for target tickers
    targets = ['BRKB', 'BFB']
    found = df[df['Ticker'].isin(targets)]
    
    if found.empty:
        print("✅ No incorrect tickers (BRKB, BFB) found. Already patched?")
    else:
        print(f"⚠️ Found {len(found)} rows with incorrect tickers:")
        print(found['Ticker'].tolist())
        
        # Apply patch
        df['Ticker'] = df['Ticker'].replace({
            'BRKB': 'BRK.B',
            'BFB': 'BF.B'
        })
        
        # Save back
        df.to_csv(CSV_PATH, index=False)
        print(f"✅ patched and saved to {CSV_PATH}")
        
    # Verify result
    df_new = pd.read_csv(CSV_PATH)
    if 'BRK.B' in df_new['Ticker'].values:
        print("🎉 Verification Success: BRK.B exists in financials.csv")
    else:
        print("❌ Verification Failed: BRK.B still missing")

if __name__ == "__main__":
    patch_financials()
