
import os
import sys
import pandas as pd
import yfinance as yf
import json
from datetime import datetime, timedelta
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from scripts.config import PATHS, FETCH_MAP

def update_financials(mode='smart'):
    print(f"\n💰 [Financials Update] Starting... (Mode: {mode})")
    
    # 1. Load existing financials
    csv_path = PATHS['FINANCIAL_INFO']
    if os.path.exists(csv_path):
        df_fin = pd.read_csv(csv_path)
        # Ensure Ticker is string
        df_fin['Ticker'] = df_fin['Ticker'].astype(str)
        # Create a list of existing tickers
        existing_tickers = df_fin['Ticker'].tolist()
        df_fin.set_index('Ticker', inplace=True)
    else:
        print("⚠️ financials.csv not found. Will create new.")
        df_fin = pd.DataFrame(columns=['PER', 'Forward_PER', 'PBR', 'PSR', 'EV_EBITDA', 'ROE', 'Profit_Margin', 'Oper_Margin', 'Rev_Growth', 'EPS_Growth', 'Sector'])
        df_fin.index.name = 'Ticker'
        existing_tickers = []

    # 2. Determine target tickers
    targets = []
    
    if mode == 'smart':
        # Check calendar_data.json for earnings
        cal_path = os.path.join(os.path.dirname(csv_path), 'calendar_data.json')
        if os.path.exists(cal_path):
            with open(cal_path, 'r', encoding='utf-8') as f:
                cal_data = json.load(f)
            
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            two_days_ago = today - timedelta(days=2)
            
            today_str = today.strftime('%Y-%m-%d')
            yesterday_str = yesterday.strftime('%Y-%m-%d')
            days_ago_2_str = two_days_ago.strftime('%Y-%m-%d')
            
            target_dates = [today_str, yesterday_str, days_ago_2_str]
            
            print(f"🔎 Checking earnings events for {target_dates} (server time)...")
            
            for ticker, data in cal_data.items():
                # Check next_earnings or last_earnings_date
                last_date = data.get('last_earnings_date')
                next_date = data.get('next_earnings')
                
                # Logic: If earnings happened recently (up to 2 days ago to cover timezones/delays)
                is_target = False
                if last_date in target_dates:
                    is_target = True
                elif next_date in target_dates: 
                    is_target = True
                    
                if is_target:
                    targets.append(ticker)
        else:
            print("⚠️ calendar_data.json not found. Skipping smart update.")
            
    elif mode == 'all':
        # Update ALL existing tickers (plus any new ones if passed/found?)
        # For now, just refresh existing list
        targets = existing_tickers
        if not targets:
            # Fallback if empty file
            targets = ['AAPL', 'MSFT', 'GOOGL'] # minimal fallback
        
    targets = list(set(targets))
    
    # Also ensure we include BRK.B if it's in target
    
    if not targets:
        print("✨ No targets to update.")
        return

    print(f"🎯 Targets to update ({len(targets)}): {targets[:10]}..." if len(targets) > 10 else f"🎯 Targets to update ({len(targets)}): {targets}")
    
    # 3. Prepare Fetch Map
    # Map: Fetch Ticker -> Original Ticker
    # e.g. 'BRK-B' -> 'BRK.B'
    fetch_map_list = {} # {yf_ticker: original_ticker}
    yf_tickers_list = []
    
    for t in targets:
        # Use FETCH_MAP from config first, else simple replace
        if t in FETCH_MAP:
            yf_sym = FETCH_MAP[t]
        else:
            yf_sym = t.replace('.', '-')
            
        fetch_map_list[yf_sym] = t
        yf_tickers_list.append(yf_sym)
    
    # 4. Batch Fetch
    chunk_size = 50
    updated_count = 0
    
    for i in range(0, len(yf_tickers_list), chunk_size):
        chunk = yf_tickers_list[i:i+chunk_size]
        print(f"   Fetching batch {i//chunk_size + 1}/{len(yf_tickers_list)//chunk_size + 1} ({len(chunk)} stocks)...")
        
        try:
            batch = yf.Tickers(" ".join(chunk))
            
            # yf.Tickers.tickers is dict {sym: Ticker}
            # Note: keys in batch.tickers might be upper case or standardized
            
            for yf_sym, ticker_obj in batch.tickers.items():
                try:
                    # Find original ticker
                    # batch.tickers keys usually match the input list, but sometimes yf normalizes
                    original_ticker = fetch_map_list.get(yf_sym, fetch_map_list.get(yf_sym.upper()))
                    
                    if not original_ticker:
                        # Reverse lookup fallback (unlikely needed)
                        continue

                    info = ticker_obj.info
                    if not info:
                        continue
                    
                    # Mapping fields
                    # We only update fields if they exist in info
                    fields = {
                        'PER': 'trailingPE',
                        'Forward_PER': 'forwardPE',
                        'PBR': 'priceToBook',
                        'PSR': 'priceToSalesTrailing12Months',
                        'EV_EBITDA': 'enterpriseToEbitda',
                        'ROE': 'returnOnEquity',
                        'Profit_Margin': 'profitMargins',
                        'Oper_Margin': 'operatingMargins',
                        'Rev_Growth': 'revenueGrowth',
                        'EPS_Growth': 'earningsGrowth',
                        'Sector': 'sector'
                    }
                    
                    for csv_col, yf_key in fields.items():
                        if yf_key in info and info[yf_key] is not None:
                            df_fin.at[original_ticker, csv_col] = info[yf_key]
                            
                    updated_count += 1
                    
                except Exception as e:
                    # print(f"   ⚠️ Error extracting {yf_sym}: {e}")
                    pass
                    
        except Exception as e:
            print(f"   ❌ Batch fetch failed: {e}")

    # 5. Save
    # Sort by Ticker
    df_fin.sort_index(inplace=True)
    
    # Reset index to save Ticker column
    df_fin.to_csv(csv_path, index=True)
    print(f"✅ Updated financials for {updated_count} stocks. Saved to {csv_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='smart', choices=['smart', 'all'])
    args = parser.parse_args()
    
    update_financials(mode=args.mode)
