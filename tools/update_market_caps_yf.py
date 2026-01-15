import yfinance as yf
import json
import concurrent.futures
import time

def fetch_mc(ticker):
    try:
        # Normalize for yfinance
        sym = ticker.replace('.', '-')
        t = yf.Ticker(sym)
        mc = t.fast_info['market_cap']
        return ticker, int(mc)
    except Exception as e:
        print(f"  ⚠ Error for {ticker}: {e}")
        return ticker, None

def update_market_caps():
    print("🚀 Fetching market cap data using yfinance fast_info (threaded)...")
    
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ data.json not found")
        return

    tickers = [d['ticker'] for d in data]
    print(f"Processing {len(tickers)} tickers...")
    
    mc_map = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_mc, t): t for t in tickers}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            ticker, mc = future.result()
            if mc:
                mc_map[ticker] = mc
            completed += 1
            if completed % 50 == 0:
                print(f"  Progress: {completed}/{len(tickers)}")
                
    # Update data
    print("\nApplying updates...")
    updated_count = 0
    for item in data:
        t = item['ticker']
        if t in mc_map:
            item['market_cap'] = mc_map[t]
            updated_count += 1
            
    # Save details
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated market caps for {updated_count} stocks.")

if __name__ == "__main__":
    update_market_caps()
