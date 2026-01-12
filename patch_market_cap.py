
import json
import yfinance as yf
import os

def patch_market_caps():
    print("🩹 Patching data.json with Market Caps...")
    
    if not os.path.exists('data.json'):
        print("❌ data.json not found.")
        return

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    updated_count = 0
    total = len(data)
    
    # Collect all tickers
    tickers = [item['ticker'] for item in data]
    
    # Fetch all at once? No, fast_info is per ticker object.
    # Parallelizing? Threading is good for IO.
    # But for simplicity, simple loop.
    
    print(f"💰 Fetching Market Caps for {total} items...")
    
    import concurrent.futures
    
    def fetch_mcap(ticker):
        try:
            yf_t = ticker.replace('.', '-')
            # specific fix for BRK.B
            if ticker == 'BRK.B': yf_t = 'BRK-B'
            
            mcap = yf.Ticker(yf_t).fast_info.get('market_cap', 0)
            return ticker, mcap
        except:
            return ticker, 0

    mcap_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_mcap, t): t for t in tickers}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            t, mcap = future.result()
            mcap_map[t] = mcap
            if i % 50 == 0: print(f"   [{i}/{total}] Fetched...", end='\r')

    # Update data
    for item in data:
        t = item['ticker']
        if t in mcap_map:
            item['market_cap'] = mcap_map[t]
            updated_count += 1
            
    # Save
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\n✅ Patched {updated_count} items in data.json")

if __name__ == "__main__":
    patch_market_caps()
