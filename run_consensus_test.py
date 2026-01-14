import json
import time
from fetch_sp500 import fetch_consensus_data

# Top 10 Tickers to test
TEST_TICKERS = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "AMD", "INTC", "NFLX"]

def run_test():
    print("🚀 Starting Consensus Data Test...")
    
    # Load existing data
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"📖 Loaded data.json ({len(data)} items)")
    except FileNotFoundError:
        print("❌ data.json not found. Run full fetch first.")
        return

    updated_count = 0
    
    # Create a map for quick access
    data_map = {item['ticker']: item for item in data}

    for ticker in TEST_TICKERS:
        if ticker not in data_map:
            print(f"⚠️ {ticker} not found in data.json, skipping.")
            continue
            
        print(f"\n🔍 Fetching Consensus for {ticker}...")
        
        # Call the actual function from fetch_sp500.py
        consensus = fetch_consensus_data(ticker)
        
        if consensus:
            print(f"   ✅ Success: Target ${consensus['target_price']['mean']}, Score {consensus['recommendation']['score']} ({consensus['recommendation']['status']})")
            
            # Update data
            if 'context' not in data_map[ticker]:
                data_map[ticker]['context'] = {}
            
            data_map[ticker]['context']['consensus'] = consensus
            
            # Also update flattened structure if needed (page.html uses data.consensus if mapped in main loop)
            # In fetch_sp500.py, 'consensus' is added to 'context' then mapped to 'consensus' key in final json.
            # So here we should update the top-level key as well if data.json is final output.
            data_map[ticker]['consensus'] = consensus
            
            updated_count += 1
        else:
            print(f"   ❌ Failed to fetch data (Result is None)")
            
        # Rate limit (3.1s covers the 20/min limit)
        # For 10 items, it will take ~30 seconds.
        time.sleep(3.1)

    # Save updated data
    if updated_count > 0:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(list(data_map.values()), f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved updated data.json with {updated_count} consensus records.")
    else:
        print("\n⚠️ No data updated.")

if __name__ == "__main__":
    run_test()
