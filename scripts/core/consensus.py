import yfinance as yf
import json
import time
import os
import socket
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
        
        # Dual class handling is already done in fetcher, but yfinance logic needs care
        # Fetcher returns 'BRK.B', yfinance needs 'BRK-B'
        
        success_count = 0
        fail_count = 0
        consensus_map = {}
        
        print(f"🚀 Starting Consensus Fetch for {len(tickers)} stocks...")
        print("⏳ This process will take time (approx 30 mins) to avoid rate limits.")
        
        for idx, ticker in enumerate(tickers):
            # Convert to Yahoo format (Dot to Hyphen)
            # Fetcher's fetch_map handles this but let's be explicit
            yf_ticker = ticker.replace('.', '-')
            
            print(f"[{idx+1}/{len(tickers)}] Fetching {ticker} ({yf_ticker})...", end='', flush=True)
            
            try:
                stock = yf.Ticker(yf_ticker)
                info = stock.info
                
                # Check availability
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
                    print(f" ✅ {status} ({score}) + Financials")
                    success_count += 1
                else:
                    # Partial Data
                    target_mean = info.get('targetMeanPrice')
                    has_financial = any(v != 0 for v in financial_health.values())
                    
                    if target_mean or has_financial:
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
                            print(f" ⚠️ No rating, but saved target price ${target_mean}")
                        else:
                            print(f" ⚠️ No consensus, but saved financials")
                        success_count += 1
                    else:
                        print(f" ⚠️ No data (Info empty)")
                        fail_count += 1
                    
                fail_count += 1
            except Exception as e:
                print(f" ❌ CRITICAL ERROR fetching {ticker}: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
                
            # Rate Limiting: 2 seconds per stock
            time.sleep(2)
            
        print(f"\n✅ Loop Finished. processed {len(tickers)} items.")
        
        # Save to JSON using PATHS
        try:
            print(f"💾 Saving to {self.output_path}...")
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(consensus_map, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Saved consensus + financial data for {len(consensus_map)} stocks to {self.output_path}")
            print(f"📊 Summary: Success {success_count}, Fail {fail_count} (Total {len(tickers)})")
        except Exception as e:
            print(f"❌ FAILED TO SAVE JSON: {e}")
            import traceback
            traceback.print_exc()
