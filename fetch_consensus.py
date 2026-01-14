import yfinance as yf
import json
import time
import FinanceDataReader as fdr
import os
from datetime import datetime

# 1. Get S&P 500 List
def get_sp500_tickers():
    try:
        sp500 = fdr.StockListing('SP500')
        tickers = sp500['Symbol'].tolist()
        return tickers
    except:
        return ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "TSLA"]

def fetch_all_consensus():
    tickers = get_sp500_tickers()
    
    # Dual class handling (similar to fetch_sp500.py)
    # yfinance uses '-' (BRK-B), FDR uses '.' (BRK.B)
    # We need to ensure we query yfinance with hyphens, but save with dots to match fetch_sp500.py
    
    # Statistics
    success_count = 0
    fail_count = 0
    
    print(f"🚀 Starting Consensus Fetch for {len(tickers)} stocks...")
    print("⏳ This process will take time (approx 30 mins) to avoid rate limits.")
    
    for idx, ticker in enumerate(tickers):
        # Convert to Yahoo format
        yf_ticker = ticker.replace('.', '-')
        
        print(f"[{idx+1}/{len(tickers)}] Fetching {ticker} ({yf_ticker})...", end='', flush=True)
        
        try:
            stock = yf.Ticker(yf_ticker)
            # Force a request to initialize? 
            # Sometimes info is lazy properly, but accessing keys triggers it.
            info = stock.info
            
            # Check availability
            # Recommendation Mean: 1 (Strong Buy) - 5 (Strong Sell)
            # We want to reverse it: 5 (Strong Buy) - 1 (Strong Sell)
            rec_mean_yahoo = info.get('recommendationMean')
            
            if rec_mean_yahoo:
                # Invert Score: NewScore = 6 - YahooScore
                score = round(6 - rec_mean_yahoo, 1)
                
                # Determine Status based on converted score
                if score >= 4.5: status = "Strong Buy"
                elif score >= 3.5: status = "Buy"
                elif score >= 2.5: status = "Hold"
                elif score >= 1.5: status = "Sell"
                else: status = "Strong Sell"
                
                consensus_data = {
                    "target_price": {
                        "low": info.get('targetLowPrice'),
                        "mean": info.get('targetMeanPrice'),
                        "high": info.get('targetHighPrice')
                    },
                    "recommendation": {
                        "score": score,
                        "status": status,
                        "yahoo_mean": rec_mean_yahoo,
                        "key": info.get('recommendationKey')
                    },
                    "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                consensus_map[ticker] = consensus_data
                print(f" ✅ {status} ({score})")
                success_count += 1
            else:
                print(f" ⚠️ No data (Info empty)")
                fail_count += 1
                
        except Exception as e:
            print(f" ❌ Error: {e}")
            fail_count += 1
            
        # Rate Limiting: 2 seconds per stock
        time.sleep(2)
        
    # Save to JSON
    with open('consensus_data.json', 'w', encoding='utf-8') as f:
        json.dump(consensus_map, f, indent=2, ensure_ascii=False)
        
    print(f"\n💾 Saved consensus data for {len(consensus_map)} stocks to consensus_data.json")
    print(f"📊 Summary: Success {success_count}, Fail {fail_count} (Total {len(tickers)})")

if __name__ == "__main__":
    fetch_all_consensus()
