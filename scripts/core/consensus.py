import yfinance as yf
import json
import time
import os
import socket
import gc
from datetime import datetime
from scripts.config import PATHS
from scripts.core.fetcher import StockDataFetcher

class ConsensusManager:
    """
    Manages fetching and storing Wall St. Consensus data
    from Yahoo Finance (Recommendation Mean, Target Price, etc.)
    """
    
    def __init__(self):
        self.fetcher = StockDataFetcher()
        self.output_path = PATHS['CONSENSUS_JSON']
        # Set global timeout for yfinance downloads (30 seconds)
        socket.setdefaulttimeout(30)
        
    def fetch_all_consensus(self):
        """Fetch consensus data for all S&P 500 tickers"""
        tickers = self.fetcher.get_sp500_tickers()
        
        # 1. Load existing data to prevent data loss (Merge logic)
        consensus_map = {}
        if os.path.exists(self.output_path):
            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    consensus_map = json.load(f)
                print(f"📂 Loaded existing consensus data for {len(consensus_map)} stocks.")
            except Exception as e:
                print(f"⚠️ Failed to load existing data: {e}. Starting fresh.")
                consensus_map = {}
        
        success_count = 0
        fail_count = 0
        
        print(f"🚀 Starting Consensus Fetch for {len(tickers)} stocks...")
        print("⏳ This process will take time (approx 30 mins) to avoid rate limits.")
        
        for idx, ticker in enumerate(tickers):
            # Explicit GC every 50 stocks to prevent memory leaks in GitHub Actions
            if idx % 50 == 0:
                gc.collect()

            # [RESUME LOGIC] Check if we already have fresh data for this ticker
            today_str = datetime.now().strftime('%Y-%m-%d')
            if ticker in consensus_map:
                last_updated = consensus_map[ticker].get('last_updated', '')
                # If last_updated starts with today's date, skip it
                if last_updated.startswith(today_str):
                    print(f"[{idx+1}/{len(tickers)}] Skipping {ticker} (Already updated today: {last_updated})")
                    success_count += 1 # Count as success to keep stats happy
                    continue

            # Convert to Yahoo format (Dot to Hyphen)
            yf_ticker = ticker.replace('.', '-')
            
            print(f"[{idx+1}/{len(tickers)}] Fetching {ticker} ({yf_ticker})...")
            
            # Retry Loop (Max 3 attempts)
            max_retries = 3
            fetched_success = False
            
            for attempt in range(max_retries):
                try:
                    stock = yf.Ticker(yf_ticker)
                    info = stock.info
                    
                    # Check availability (Key check)
                    # If this succeeds, we assume fetch worked
                    rec_mean_yahoo = info.get('recommendationMean')
                    
                    # Financial Health Data
                    financial_health = {
                        "per": round(info.get('trailingPE') or 0, 2),
                        "pbr": round(info.get('priceToBook') or 0, 2),
                        "revenue_growth": round((info.get('revenueGrowth') or 0) * 100, 1),
                        "eps_growth": round((info.get('earningsGrowth') or 0) * 100, 1),
                        "roe": round((info.get('returnOnEquity') or 0) * 100, 1),
                        "operating_margin": round((info.get('operatingMargins') or 0) * 100, 1),
                        "debt_ratio": round(info.get('debtToEquity') or 0, 1),
                        "current_ratio": round(info.get('currentRatio') or 0, 2)
                    }
                    
                    # Process Data
                    if rec_mean_yahoo:
                        # Invert Score: NewScore = 6 - YahooScore
                        score = round(6 - rec_mean_yahoo, 1)
                        
                        # Status
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
                            "financial_health": financial_health,
                            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        consensus_map[ticker] = consensus_data
                        print(f"   ✅ {status} ({score})")
                        
                    else:
                        # Partial Data Logic
                        target_mean = info.get('targetMeanPrice')
                        has_financial = any(v != 0 for v in financial_health.values())
                        
                        if target_mean or has_financial:
                            # Keep existing Recommendation if we fail to get a new one? 
                            # For now, just save what we got, but careful not to overwrite good data with bad?
                            # Decision: Overwrite with what we found, assuming it's fresher.
                            
                            consensus_map[ticker] = {
                                "target_price": {
                                    "low": info.get('targetLowPrice'),
                                    "mean": target_mean,
                                    "high": info.get('targetHighPrice')
                                } if target_mean else None,
                                "recommendation": None,
                                "financial_health": financial_health if has_financial else None,
                                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            if target_mean:
                                print(f"   ⚠️ No rating, but saved target price ${target_mean}")
                            else:
                                print(f"   ⚠️ No consensus, but saved financials")
                        else:
                            print(f"   ⚠️ No data (Info empty)")
                            # Do NOT increment success/fail here yet, continue to logic end
                            pass
                    
                    fetched_success = True
                    success_count += 1
                    break # Break retry loop
                    
                except Exception as e:
                    # Check for Rate Limit specifically if possible, though 'e' might be generic
                    error_msg = str(e).lower()
                    import traceback
                    
                    is_rate_limit = "too many requests" in error_msg or "rate limit" in error_msg or "429" in error_msg
                    
                    if attempt < max_retries - 1:
                        wait_time = 10 if is_rate_limit else 2
                        print(f" ⚠️ Error (Attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        print(f" ❌ CRITICAL ERROR fetching {ticker}: {e}")
                        # traceback.print_exc() # detailed trace only on final fail
                        fail_count += 1
            
            # End of Retry Loop
            
            # Rate Limiting: 2 seconds per stock (Standard)
            time.sleep(2)
            
            # Incremental Save (Every 20 stocks)
            if (idx + 1) % 20 == 0:
                print(f"   💾 [Auto-Save] Saving progress for {len(consensus_map)} stocks...")
                try:
                    with open(self.output_path, 'w', encoding='utf-8') as f:
                        json.dump(consensus_map, f, indent=2, ensure_ascii=False)
                    # Force flush to disk
                    f.flush()
                    os.fsync(f.fileno()) 
                except: pass

        print(f"\n✅ Loop Finished. processed {len(tickers)} items.")
        
        # Final Save
        try:
            print(f"💾 Saving final data to {self.output_path}...")
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(consensus_map, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Saved consensus + financial data for {len(consensus_map)} stocks to {self.output_path}")
            print(f"📊 Summary: Success {success_count}, Fail {fail_count} (Total {len(tickers)})")
        except Exception as e:
            print(f"❌ FAILED TO SAVE JSON: {e}")
            import traceback
            traceback.print_exc()
